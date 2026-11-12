"""Single source of truth for VO-fit time inserts in the segment clips.

The animation keys were authored on a base timeline. When the estimated
(not yet recorded) Vietnamese VO for a cue is longer than its picture slot,
time is INSERTED at a moment where the machine state is steady (constant rpm,
lever held, host on screen), so nothing speeds up or freezes: the held state
simply lasts longer. build_segments.py shifts every key, the scene writes the
inserts into the root node so callouts/blinks shift the same way, and
make_segment_srt.py shifts the cue times identically.
"""
INSERTS = {
    "sc03": [(5.0, 1.0), (19.0, 0.6), (23.0, 1.5)],
    "sc04": [(2.0, 0.5), (8.0, 1.8), (14.0, 1.8), (26.5, 1.1)],
    "sc05": [(3.0, 1.3), (12.5, 1.4), (16.5, 2.8), (21.5, 0.8)],
}


def warp(seg, t):
    return t + sum(dt for at, dt in INSERTS.get(seg, []) if t > at)


def extra(seg):
    return sum(dt for _, dt in INSERTS.get(seg, []))
