"""Machine joint motion for the EP02 full episode (shared rig, tools/kinematics.py).

Moves are flow-controlled: the ACTUATING CYLINDER's length follows a smooth
trapezoid (min-jerk ramps), and the joint angle is solved from that length by
bisection on the pin geometry - so rods never jump and links stay rigid.
"""
import math
import numpy as np
from kinematics import fk, ik, RIG

G = RIG["ground_y"]
JOINTS = ("boom_deg", "arm_rel", "bucket_rel")
CYL = {"boom_deg": "Lb", "arm_rel": "La", "bucket_rel": "Lk"}


def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)


def trapezoid(u, ramp=0.22):
    """normalised distance 0..1 for a speed profile with smooth ramps"""
    u = min(max(u, 0.0), 1.0)
    grid = np.linspace(0, 1, 401)
    sp = np.array([smooth(g / ramp) if g < ramp else (1 - smooth((g - 1 + ramp) / ramp) if g > 1 - ramp else 1.0) for g in grid])
    cum = np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) * 0.5 * np.diff(grid))])
    return float(np.interp(u, grid, cum / cum[-1]))


def solve(joint, pose, L):
    """angle of `joint` (others fixed) giving cylinder length L"""
    i = JOINTS.index(joint)
    lo, hi = -40.0, 170.0
    f = lambda a: fk(*[a if k == i else pose[k] for k in range(3)])[CYL[joint]]
    # bracket on monotone side around the current angle
    a0 = pose[i]
    lo, hi = a0 - 80, a0 + 80
    flo, fhi = f(lo), f(hi)
    inc = fhi > flo
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if (f(mid) < L) == inc:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


class Motion:
    def __init__(self, pose):
        self.start = tuple(pose)
        self.segs = []          # (t0, t1, fn(t, pose_at_t0) -> pose)

    def end_pose(self):
        return self.pose(1e9)

    def pose(self, t):
        p = self.start
        for t0, t1, fn in self.segs:
            if t < t0:
                break
            p = fn(min(t, t1), p)
        return p

    def move(self, t0, dur, targets, ramp=0.22, settle=0.0):
        """move joints to targets (dict joint->deg); each joint's cylinder length
        is interpolated with the same trapezoid -> simultaneous, smooth"""
        t1 = t0 + dur
        def fn(t, p0, t0=t0, t1=t1, targets=targets):
            u = trapezoid((t - t0) / (t1 - t0), ramp)
            p = list(p0)
            for j, a1 in targets.items():
                i = JOINTS.index(j)
                pe = list(p0)
                pe[i] = a1
                L0 = fk(*p0)[CYL[j]]
                L1 = fk(*[a1 if k == i else p0[k] for k in range(3)])[CYL[j]]
                p[i] = solve(j, [p[k] if k != i else p0[i] for k in range(3)], L0 + (L1 - L0) * u)
            if settle and t >= t1 - 1e-9:
                pass
            return tuple(p)
        self.segs.append((t0, t1, fn))
        return t1

    def path(self, t0, waypoints):
        """bucket-tip path (V3/V4 scoop): waypoints [(dt, (x, y), phi)], ik per sample"""
        ts = [t0 + w[0] for w in waypoints]
        P = [np.array([*w[1], w[2]], float) for w in waypoints]
        def cat(p0, p1, p2, p3, u):
            return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
        def fn(t, p0):
            for i in range(len(ts) - 1):
                if ts[i] <= t <= ts[i + 1]:
                    u = (t - ts[i]) / (ts[i + 1] - ts[i])
                    if i in (0, len(ts) - 2):
                        u = u * u * (3 - 2 * u)
                    x, y, ph = cat(P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)], u)
                    return ik((x, y), ph)
            return ik(tuple(P[-1][:2]), P[-1][2]) if t > ts[-1] else ik(tuple(P[0][:2]), P[0][2])
        self.segs.append((ts[0], ts[-1], fn))
        return ts[-1]

    def keys(self, t_end, path="World/Machine", hz=15.0):
        """dense linear keys for the three joint tracks"""
        out = {f"{path}:{j}": [] for j in JOINTS}
        n = int(t_end * hz) + 1
        for k in range(n + 1):
            t = min(k / hz, t_end)
            p = self.pose(t)
            for j, v in zip(JOINTS, p):
                out[f"{path}:{j}"].append((round(t, 4), round(float(v), 4), 1.0))
        return out


# V3/V4 scoop (bucket tooth tip, machine px; tooth direction deg) relative times
SCOOP = [(0.0, (668, G - 38), 110), (1.6, (602, G - 44), 128), (3.0, (532, G - 42), 150),
         (4.1, (482, G - 98), 195), (5.1, (468, G - 140), 200)]
