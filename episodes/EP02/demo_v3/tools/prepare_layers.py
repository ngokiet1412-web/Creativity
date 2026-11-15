"""Cut rigid layers for the EP02 V3 rig.

Machine parts come from the committed ImageGen atlas (../demo/godot/art/pc200-parts.png).
Each connected alpha component becomes one rigid layer; pins are measured on the
atlas with HoughCircles and stored in parts.json. The bucket is mirrored left-right
so its opening faces the cab, as on a backhoe. Mirroring and uniform scale only.

Crew layers are cut from the local EP01 still `field-reply.png` (not in the public
repo) with OpenCV GrabCut, then split into base / Capy head / collar overlay.

usage: python3 prepare_layers.py ATLAS FIELD_REPLY OUT_ART OUT_LOCAL
"""
import json, sys
import cv2
import numpy as np
from PIL import Image

atlas_path, field_path, out_art, out_local = sys.argv[1:5]

# ---------------------------------------------------------------- machine parts
A = np.array(Image.open(atlas_path).convert("RGBA"))
alpha = A[..., 3]
n, lab, st, _ = cv2.connectedComponentsWithStats((alpha > 8).astype(np.uint8))

# Atlas pins (px), measured with HoughCircles on the atlas, see TECHNICAL_QA_V3.md
PARTS = {
    "upper": {"seed": (441, 368), "pins": {"boom_foot": (725.5, 475.5)}},
    "undercarriage": {"seed": (504, 839), "pins": {}},
    "boom": {"seed": (1138, 203), "pins": {"foot": (893.5, 391.5), "tip": (1470.5, 83.5),
                                            "top_lug": (1202.5, 101.5), "under_lug": (1321.5, 173.5)}},
    "arm": {"seed": (1183, 485), "pins": {"elbow": (1138.5, 353.5), "wrist": (1236.5, 640.5)}},
    "bucket": {"seed": (1206, 871), "pins": {"hinge": (1118.5, 720.5), "tooth_tip": (1449.0, 916.0)},
               "mirror": True},
}
meta = {"source": "../demo/godot/art/pc200-parts.png", "parts": {}}
for name, p in PARTS.items():
    sx, sy = p["seed"]
    label = lab[sy, sx]
    if label == 0:  # seed on a hole: take the largest component overlapping a window
        win = lab[sy - 20:sy + 20, sx - 20:sx + 20]
        vals, counts = np.unique(win[win > 0], return_counts=True)
        label = vals[np.argmax(counts)]
    x, y, w, h = st[label, :4]
    pad = 4
    x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
    crop = A[y0:y1, x0:x1].copy()
    keep = lab[y0:y1, x0:x1] == label
    crop[..., 3] = np.where(keep, crop[..., 3], 0)
    pins = {k: [v[0] - x0, v[1] - y0] for k, v in p["pins"].items()}
    if p.get("mirror"):
        crop = crop[:, ::-1].copy()
        W = crop.shape[1]
        pins = {k: [W - 1 - v[0], v[1]] for k, v in pins.items()}
    Image.fromarray(crop).save(f"{out_art}/{name}.png")
    bottom = int(np.nonzero(crop[..., 3].max(1) > 128)[0].max())
    meta["parts"][name] = {"size": [crop.shape[1], crop.shape[0]], "atlas_rect": [int(x0), int(y0), int(x1 - x0), int(y1 - y0)],
                           "pins": pins, "mirrored": bool(p.get("mirror")), "opaque_bottom": bottom}
json.dump(meta, open(f"{out_art}/parts.json", "w"), indent=1)
print(json.dumps(meta["parts"], indent=1))

# ----------------------------------------------------------------- crew layers
img = cv2.imread(field_path)
h, w = img.shape[:2]
mask = np.zeros((h, w), np.uint8)
bgd = np.zeros((1, 65)); fgd = np.zeros((1, 65))
cv2.grabCut(img, mask, (0, 240, w - 1, h - 241), bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
k, lab2, st2, _ = cv2.connectedComponentsWithStats(m)
m = np.zeros_like(m)
for i in range(1, k):
    if st2[i, 4] > 3000:
        m[lab2 == i] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
ff = m.copy(); cv2.floodFill(ff, None, (0, 0), 255); m = m | cv2.bitwise_not(ff)
m = cv2.GaussianBlur(m, (3, 3), 0)
rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
yy, xx = np.mgrid[0:h, 0:w]
capy_zone = (xx >= 318) & (yy >= 386)
head = capy_zone & (yy < 562)
collar = capy_zone & (yy >= 540) & (yy < 600)

def layer(sel):
    out = rgba.copy(); out[..., 3] = np.where(sel, m, 0); return out

Image.fromarray(layer(~head)).save(f"{out_local}/crew_base.png")
Image.fromarray(layer(head)).save(f"{out_local}/capy_head.png")
Image.fromarray(layer(collar)).save(f"{out_local}/capy_collar.png")
crew = {"source": "field-reply.png (EP01 V7 G-02 still, local)", "size": [w, h],
        "capy_head_pivot": [414, 556],
        "capy_eyes": [[369, 454, 7, 10.5], [428, 472, 7.5, 10]],
        "engineer_eyes": [[135, 368, 7, 11], [185, 354, 6, 10]],
        "fur": [250, 172, 100]}
json.dump(crew, open(f"{out_local}/crew.json", "w"), indent=1)
