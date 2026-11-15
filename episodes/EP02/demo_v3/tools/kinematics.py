"""Shared forward/inverse kinematics for the EP02 V3 rig (mirrors godot/rig.gd)."""
import json, math, os
import numpy as np
RIG = json.load(open(os.path.join(os.path.dirname(__file__), "..", "godot", "art", "rig.json")))
L1, L2 = RIG["boom_len"], RIG["arm_len"]
H = np.array(RIG["bucket_sprite"]["hinge"]); TT = np.array(RIG["bucket_sprite"]["tip"])
MK = RIG["bucket_tip_len"] / np.linalg.norm(TT - H)
TIP_LOCAL = (TT - H) * MK
K_LOCAL = np.array(RIG["bucket_sprite"]["link_boss_offset_px"]) * MK
TIP_ANG = math.degrees(math.atan2(TIP_LOCAL[1], TIP_LOCAL[0]))
G = RIG["ground_y"]

def R(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s], [s, c]])

def fk(boom_deg, arm_rel_deg, bucket_rel_deg):
    ab = math.radians(-boom_deg)
    W1 = R(ab) @ np.array([L1, 0.0])
    aa = ab + math.radians(arm_rel_deg)
    W2 = W1 + R(aa) @ np.array([L2, 0.0])
    bk = aa + math.radians(bucket_rel_deg - 90.0)
    arm = lambda p: W1 + R(aa) @ np.array(p, float)
    boom = lambda p: R(ab) @ np.array(p, float)
    bucket = lambda p: W2 + R(bk) @ np.array(p, float)
    bc = RIG["boom_cyl"]; ac = RIG["arm_cyl"]; kc = RIG["bucket_cyl"]
    Bb, Eb = np.array(bc["base_upper"], float), boom(bc["eye_boom"])
    Ab, Ea = boom(ac["base_boom"]), arm(ac["eye_arm"])
    C, S, K = arm(kc["base_arm"]), arm(kc["side_pivot_arm"]), bucket(K_LOCAL)
    a, b = kc["side_len"], kc["h_len"]
    d = np.linalg.norm(K - S); x = (a * a - b * b + d * d) / (2 * d)
    h = math.sqrt(max(a * a - x * x, 0.0)); u = (K - S) / d; v = np.array([-u[1], u[0]])
    J = S + u * x - v * h          # fixed branch (outer side of the arm)
    return dict(W1=W1, W2=W2, T=bucket(TIP_LOCAL), K=K, S=S, C=C, J=J, Bb=Bb, Eb=Eb, Ab=Ab, Ea=Ea,
                Lb=np.linalg.norm(Eb - Bb), La=np.linalg.norm(Ea - Ab), Lk=np.linalg.norm(J - C),
                reach_ok=abs(a - b) < d < a + b, ab=ab, aa=aa, bk=bk,
                heel=bucket(np.array([0.0, 0.0])))

def ik(T, phi_deg):
    bk = math.radians(phi_deg - TIP_ANG)
    W2 = np.array(T, float) - R(bk) @ TIP_LOCAL
    D = np.linalg.norm(W2)
    c = (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D)
    if abs(c) > 1: raise ValueError("unreachable")
    ab = math.atan2(W2[1], W2[0]) - math.acos(c)
    W1 = R(ab) @ np.array([L1, 0.0])
    aa = math.atan2(*(W2 - W1)[::-1])
    return -math.degrees(ab), math.degrees(aa - ab), math.degrees(bk - aa) + 90.0
