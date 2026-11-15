"""Recover original EP01 rigid layers locally; exclude the adjacent mascot.
Original source files and cutouts never enter the public repository.
"""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image

DEMO = Path(__file__).resolve().parents[2]
LOCAL = DEMO / 'godot/local'
SOURCE = DEMO.parent / 'demo/godot/local/field-reply.png'
LOCAL.mkdir(exist_ok=True)
img = cv2.imread(str(SOURCE))
h, w = img.shape[:2]
mask = np.zeros((h, w), np.uint8)
bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(img, mask, (0, 240, w - 1, h - 241), bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
ff = m.copy()
cv2.floodFill(ff, None, (0, 0), 255)
m |= cv2.bitwise_not(ff)
rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
yy, xx = np.mgrid[0:h, 0:w]
head = (xx >= 318) & (yy >= 386) & (yy < 562)
collar = (xx >= 318) & (yy >= 540) & (yy < 600)
def layer(sel):
    out = rgba.copy()
    out[..., 3] = np.where(sel, m, 0)
    return out
Image.fromarray(layer(~head)).save(LOCAL / 'crew_base.png')
Image.fromarray(layer(head)).save(LOCAL / 'capy_head.png')
Image.fromarray(layer(collar)).save(LOCAL / 'capy_collar.png')
crew = {'size': [w, h], 'capy_head_pivot': [414, 556],
        'capy_eyes': [[369, 454, 7, 10.5], [428, 472, 7.5, 10]],
        'engineer_eyes': [[135, 368, 7, 11], [185, 354, 6, 10]], 'fur': [250, 172, 100]}
(LOCAL / 'crew.json').write_text(json.dumps(crew), encoding='utf-8')
# Source engineer occupies x<312. The old wider crop included a slice of Capy.
eng_zone = (xx < 312) & (yy < 630) & ~((xx >= 275) & (yy > 470))
Image.fromarray(layer(eng_zone)[230:630, :312]).save(LOCAL / 'host_eng.png')
# The near paw reaches left of the head. Keep its full contour but trim
# the neighboring engineer's hand and the horizontal barrier.
rail_edge = np.interp(xx, [293, 301, 312, 335, 351, 366, 375, 422, 434, 452, 471, 485, 495, 500, 519],
                      [581, 621, 630, 634, 638, 637, 633, 633, 637, 639, 637, 631, 614, 575, 534])
capy_zone = (xx >= np.where(yy < 520, 312, 293)) & (yy >= 385) & (yy < rail_edge)
Image.fromarray(layer(capy_zone)[370:640, 286:]).save(LOCAL / 'host_capy.png')
print('Prepared original EP01 crew and clean host regions')
