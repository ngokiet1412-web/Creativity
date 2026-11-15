#!/usr/bin/env python3
"""Bake godot/local/studio_plate.png: the 16:9 completion of the EP01 studio cel.

The portrait cel sits flush left; the area to its right continues the cel's own
right-edge colours, blurred vertically so they read as wall / bench / desk
bands (no pixel streaks), with plank lines, a soft lamp pool and a vignette.
Alpha ramps 0 -> 1 across the last 70 px of the cel so the seam is a soft blend.
Local asset (derived from the owner's cel) - not committed to the public repo.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "..", "..", "godot", "local")
cel = np.asarray(Image.open(os.path.join(LOCAL, "studio-cels.png")).convert("RGB").crop((0, 0, 520, 737)).resize((762, 1080), Image.LANCZOS), float)
col = cel[:, -5:, :].mean(1)                                   # right-edge colour per row
img = Image.fromarray(np.repeat(col[:, None, :], 8, 1).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
col = np.asarray(img, float)[:, 4, :]
W = 1920
# wall rows: one calm navy (median of the cel's wall rows) instead of copying
# whatever object happens to touch the cel edge; bench + desk bands are kept
bench_top = 640
wallc = np.median(col[200:600], 0)
ramp = np.clip((np.arange(1080) - (bench_top - 40)) / 40.0, 0, 1)[:, None]
col = wallc[None, :] * (1 - ramp) + col * ramp
plate = np.repeat(col[:, None, :], W, 1)
x = np.arange(W)[None, :, None]
y = np.arange(1080)[:, None, None]
wall = (y < bench_top - 30)
for px in range(820, W, 96):                                   # plank joints on the wall
    plate[:, px:px + 2, :] *= np.where(wall, 0.82, 1.0)
lamp = np.exp(-(((x - 1390) / 620.0) ** 2 + ((y - 330) / 420.0) ** 2))
plate *= 0.86 + 0.22 * lamp
vig = 1.0 - 0.35 * np.clip((x - 1500) / 420.0, 0, 1) ** 2 - 0.2 * np.clip((y - 800) / 280.0, 0, 1) ** 2
plate *= vig
alpha = np.clip((np.arange(W) - 692) / 70.0, 0, 1)
alpha = alpha * alpha * (3 - 2 * alpha)
a2 = np.repeat(alpha[None, :], 1080, 0)
a2[150:589, 1010:1790] = 0.0                                   # monitor screen: a hole onto the world
out = np.dstack([np.clip(plate, 0, 255), a2 * 255]).astype(np.uint8)
Image.fromarray(out, "RGBA").save(os.path.join(LOCAL, "studio_plate.png"))
print("plate ok")
