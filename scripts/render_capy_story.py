"""Render the 20-second Capy BK story from animated layers and a 3D schematic."""

import argparse
import json
import math
from pathlib import Path
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from render_capy_multishot import ease, load_voice, render_voice
from render_capy_pilot import FPS, ROOT, SIZE, check_hash, encode_picture, posed_frames, viseme_at, warp_mouth


MANIFEST = ROOT / "episodes/EP01/story_20s.json"
STUDIO_POSES = [(0, 0), (3, 1), (10, 2), (21, 3), (36, 4), (42, 5), (51, 6), (60, 7)]


def camera(plate, zoom, dx=0, dy=0):
    width, height = plate.size
    w = min(width, height * SIZE[0] / SIZE[1]) / zoom
    h = w * SIZE[1] / SIZE[0]
    x = min(max((width - w) / 2 + dx, 0), width - w)
    y = min(max((height - h) / 2 + dy, 0), height - h)
    return plate.transform(SIZE, Image.Transform.EXTENT, (x, y, x + w, y + h), Image.Resampling.BICUBIC)


def motion_mask(size):
    mask = Image.new("L", size)
    w, h = size
    margin = max(4, min(w, h) // 12)
    ImageDraw.Draw(mask).rounded_rectangle((margin, margin, w - margin, h - margin), margin, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(margin / 2))


def move_patch(frame, box, mask, dx, dy):
    x, y, right, bottom = box
    patch = frame.transform(mask.size, Image.Transform.EXTENT, (x - dx, y - dy, right - dx, bottom - dy),
                            Image.Resampling.BICUBIC)
    frame.paste(patch, (x, y), mask)


def paint_gauge(frame, fill):
    draw = ImageDraw.Draw(frame)
    x, y = 853, 1107
    draw.ellipse((790, 1041, 916, 1168), "#20272c", outline="#42464a", width=3)
    arc = (802, 1054, 904, 1156)
    draw.arc(arc, 148, 197, "#e26b51", width=7)
    draw.arc(arc, 197, 274, "#e8c998", width=7)
    draw.arc(arc, 274, 381, "#83c9b9", width=7)
    for step in range(9):
        a = math.radians(150 + step * 28)
        draw.line((x + 40 * math.cos(a), y + 40 * math.sin(a),
                   x + 48 * math.cos(a), y + 48 * math.sin(a)), fill="#f5e4ca", width=2)
    a = math.radians(150 + 215 * fill)
    draw.line((x, y, x + 46 * math.cos(a), y + 46 * math.sin(a)), fill="#ff6949", width=6)
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill="#11171c", outline="#ef8a64", width=2)


def portrait_frames(plate, count, cues, cabin, drop):
    boxes = [(205, 752, 397, 1028), (611, 755, 798, 1028)] if cabin else [(434, 731, 648, 925)]
    masks = [motion_mask((right - x, bottom - y)) for x, y, right, bottom in boxes]
    mouth = (506, 596, 102) if cabin else (308, 687, 77)
    for i in range(count):
        t = (i + 0.5) / FPS
        progress = t / (count / FPS)
        pulse = math.exp(-((t - drop - 0.22) / 0.21) ** 2) if cabin else 0
        opening, width = viseme_at(cues, t)
        opening = max(opening, 0.69 * pulse)
        frame = warp_mouth(plate, *mouth, opening, width, radius=66 if cabin else 61)
        for j, (box, mask) in enumerate(zip(boxes, masks)):
            move_patch(frame, box, mask, 4.2 * math.sin(t * 5.3 + j),
                       (2.7 if cabin else 5.3) * math.sin(t * 6 + j))
        if cabin:
            paint_gauge(frame, 0.82 - 0.63 * ease((t - drop) / 0.29))
            if pulse > 0.35:
                d = ImageDraw.Draw(frame)
                d.line((759, 461, 775, 424), fill="#f7d38d", width=6)
                d.line((781, 485, 812, 472), fill="#f7d38d", width=6)
            yield camera(frame, 1.045 + 0.035 * ease(progress) + 0.015 * pulse,
                         11 + 3 * math.sin(t * 5), 5 * math.sin(t * 9) - 7 * pulse)
        else:
            yield camera(frame, 1.018 + 0.057 * ease(progress), -11 * progress, -16 * progress)


def excavator_frames(plate, count):
    chassis = (17, 298, 925, 1212)
    boom = (625, 505, 927, 902)
    chassis_mask = motion_mask((chassis[2] - chassis[0], chassis[3] - chassis[1]))
    boom_mask = motion_mask((boom[2] - boom[0], boom[3] - boom[1]))
    rng = np.random.default_rng(36)
    flecks = [(float(x), float(y), float(phase), int(radius)) for x, y, phase, radius in zip(
        rng.uniform(102, 476, 46), rng.uniform(1120, 1220, 46), rng.random(46), rng.integers(1, 6, 46),
    )]
    for i in range(count):
        t = i / FPS
        u = i / (count - 1)
        frame = plate.copy()
        move_patch(frame, chassis, chassis_mask, 10 * ease(u), -4 * ease(u) + 3 * math.sin(t * 17))
        move_patch(frame, boom, boom_mask, 4 * math.sin(t * 4), 7 * math.sin(t * 4))
        dust = Image.new("RGBA", plate.size)
        draw = ImageDraw.Draw(dust)
        for x, y, phase, radius in flecks:
            age = (phase + t * 0.97) % 1
            px, py = x - 125 * age, y + 22 * age - 38 * math.sin(math.pi * age)
            opacity = round(158 * math.sin(math.pi * age) ** 2)
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), (232, 161, 92, opacity))
        frame.paste(dust, (0, 0), dust)
        yield camera(frame, 1.10 - 0.055 * ease(u), -25 + 46 * u, 13 - 24 * u)


def section(a, b):
    f = a[2] / (a[2] - b[2])
    return tuple(x + (y - x) * f for x, y in zip(a, b))


def submerged(face):
    result = []
    for a, b in zip(face, face[1:] + face[:1]):
        if a[2] <= 0:
            result.append(a)
        if (a[2] < 0 < b[2]) or (b[2] < 0 < a[2]):
            result.append(section(a, b))
    return result


def tank_frames(count, font_path):
    size = (540, 960)
    top = Image.new("RGB", size, "#06121b")
    light = Image.new("RGB", size, "#244c52")
    halo = Image.new("L", size)
    ImageDraw.Draw(halo).ellipse((38, 175, 514, 702), 210)
    background = Image.composite(light, top, halo.filter(ImageFilter.GaussianBlur(94)))
    heading = ImageFont.truetype(str(font_path), 15)
    label = ImageFont.truetype(str(font_path), 16)
    footing = ImageDraw.Draw(background)
    footing.text((270, 172), "CẮT LỚP BÌNH DẦU GIẢ ĐỊNH", font=heading, fill="#bde9e7", anchor="mm")
    footing.line((115, 197, 425, 197), fill="#356368", width=1)
    for i in range(count):
        progress = i / (count - 1)
        angle = math.radians(19 * ease((progress - 0.13) * 2.3))
        c, s = math.cos(angle), math.sin(angle)

        def tilt(x, y, z):
            return x * c - z * s, y, x * s + z * c

        def project(point):
            x, y, z = point
            scale = 69 + 4 * ease(progress)
            return round(265 + scale * (x + 0.45 * y)), round(466 + scale * (0.29 * y - 0.88 * z + 0.025 * x))

        image = background.copy()
        draw = ImageDraw.Draw(image)
        # Horizontal datum lines are fixed in world space while the box rolls.
        for offset in (389, 437, 487, 535):
            draw.line((36, offset, 504, offset), fill="#214448", width=1)
        plan = [(-2.65, -0.87), (2.65, -0.87), (2.65, 0.87), (-2.65, 0.87)]
        low = [tilt(x, y, -1) for x, y in plan]
        high = [tilt(x, y, 1) for x, y in plan]
        water = [section(a, b) for a, b in zip(low, high)]
        for side in (0, 1, 3, 2):
            n = (side + 1) % 4
            face = [low[side], low[n], high[n], high[side]]
            draw.polygon([project(p) for p in face], fill="#234751", outline="#52868d", width=2)
            fill = submerged(face)
            if len(fill) >= 3:
                tone = "#196b75" if side in (0, 1) else "#2ba9ae"
                draw.polygon([project(p) for p in fill], fill=tone)
        draw.polygon([project(p) for p in water], fill="#5ce0d1", outline="#d6fff4", width=2)
        for idx in range(4):
            next_idx = (idx + 1) % 4
            draw.line((project(low[idx]), project(low[next_idx])), fill="#81b2b2", width=3)
            draw.line((project(high[idx]), project(high[next_idx])), fill="#8ebdbe", width=3)
            draw.line((project(low[idx]), project(high[idx])), fill="#719da2", width=3)

        bottom, top_sensor = tilt(1.92, 0.50, -0.81), tilt(1.92, 0.50, 0.87)
        surface = section(bottom, top_sensor)
        bx, by = project(bottom)
        sx, sy = project(surface)
        tx, ty = project(top_sensor)
        draw.line((bx, by, tx, ty), fill="#e78a46", width=7)
        draw.line((bx, by, sx, sy), fill="#ffdc8b", width=7)
        draw.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill="#ffdf9c")
        draw.line((tx, ty, tx + 35, ty - 39, 493, ty - 39), fill="#eeb278", width=2)
        draw.text((493, ty - 51), "CẢM BIẾN", font=label, fill="#ffce99", anchor="rs")
        wx, wy = project(section(tilt(-1.7, -0.36, -1), tilt(-1.7, -0.36, 1)))
        draw.line((wx, wy, 83, wy - 72, 46, wy - 72), fill="#9ff4e6", width=2)
        draw.text((46, wy - 86), "MẶT DẦU", font=label, fill="#bbfff0", anchor="ls")
        draw.text((270, 644), "BÌNH KÍN · CÙNG LƯỢNG DẦU", font=heading, fill="#bcdbd8", anchor="mm")
        yield image.resize(SIZE, Image.Resampling.BICUBIC)


def studio_reaction(source, count, cues):
    with Image.open(source) as gif:
        backdrop = camera(gif.convert("RGB"), 1.08).filter(ImageFilter.GaussianBlur(63))
    backdrop = Image.blend(backdrop, Image.new("RGB", SIZE, "#071326"), 0.52)
    w, h = SIZE[0], round(SIZE[0] * 354 / 478)
    edge = Image.new("L", (1, h))
    edge.putdata([min(255, round(255 * min(y, h - 1 - y) / 29)) for y in range(h)])
    matte = edge.resize((w, h))
    for picture in posed_frames(source, cues, count, STUDIO_POSES):
        frame = backdrop.copy()
        frame.paste(picture.resize((w, h), Image.Resampling.LANCZOS), (0, 505), matte)
        yield frame


def foley(path, count, kind, drop):
    rate = 48_000
    t = np.arange(count * (rate // FPS)) / rate
    envelope = np.minimum(1, 14 * np.minimum(t, t[-1] - t))
    if kind in ("cabin", "machine"):
        volume = 0.09 if kind == "cabin" else 0.20
        motor = np.sin(math.tau * (49 * t + 2.1 * np.sin(t * 2)))
        motor += 0.35 * np.sin(math.tau * 95 * t)
        rumble = motor * (0.75 + 0.25 * np.sin(math.tau * 6 * t))
        sound = volume * rumble * envelope
    else:
        sound = np.zeros_like(t)
    if kind in ("cabin", "studio"):
        start = drop + 0.09 if kind == "cabin" else 1.62
        age = np.maximum(t - start, 0)
        chirp = np.sin(math.tau * (840 * age - 900 * age ** 2))
        sound += 0.25 * chirp * np.exp(-age * 14) * np.minimum(age * 135, 1)
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes((sound * 32767).astype("<i2").tobytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plates", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--tokens", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    output = args.out.resolve()
    if output.exists():
        parser.error(f"Output already exists: {output}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    shots = manifest["shots"]
    plates = {}
    for shot in shots:
        asset = shot["asset"]
        if "plate" in asset:
            path = args.plates / asset["plate"]
            check_hash(path, asset["plate_sha256"])
            with Image.open(path) as source:
                plates[shot["visual"]] = source.convert("RGB")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        scratch = Path(scratch)
        stage = scratch / "story"
        stage.mkdir()
        voice = load_voice(args.model, args.tokens, manifest["voice"], scratch / "voice.json")
        for shot in shots:
            count = shot["duration_frames"]
            cues = render_voice(args.ffmpeg, voice, shot, scratch / "dry.wav", stage / shot["voice"])
            kind = shot["visual"]
            drop = max(end for _, end, _, _ in cues) - 0.57
            if kind in ("cabin", "standing"):
                frames = portrait_frames(plates[kind], count, cues, kind == "cabin", drop)
            elif kind == "machine":
                frames = excavator_frames(plates[kind], count)
            elif kind == "tank":
                frames = tank_frames(count, args.font)
            else:
                source = ROOT / shot["asset"]["source"]
                check_hash(source, shot["asset"]["sha256"])
                frames = studio_reaction(source, count, cues)
            if shot["sfx"]:
                foley(stage / shot["sfx"], count, kind, drop)
            encode_picture(args.ffmpeg, frames, stage / shot["video"])
        stage.rename(output)


if __name__ == "__main__":
    main()
