"""Render the four-shot Capy BK pilot with a local synthetic male voice."""

import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont
from piper import PiperVoice

from render_capy_pilot import FPS, ROOT, check_hash, encode_picture, studio_frames, synthesize


MANIFEST = ROOT / "episodes/EP01/pilot_multishot.json"
INK = "#302821"
AMBER = "#efad44"
OPEN_POSES = [(0, 0), (3, 1), (12, 2), (25, 3), (39, 5), (46, 7)]
CLOSE_POSES = [(0, 1), (9, 2), (21, 3), (33, 2), (45, 4), (50, 5), (58, 6), (63, 7)]


def load_voice(model, tokens, provenance, config_path):
    check_hash(model, provenance["model_sha256"])
    check_hash(tokens, provenance["tokens_sha256"])
    ids = {}
    for row in tokens.read_text(encoding="utf-8").splitlines():
        symbol, index = row.rsplit(" ", 1)
        ids.setdefault(symbol, []).append(int(index))
    config = {
        "audio": {"sample_rate": 22050}, "espeak": {"voice": "vi"},
        "num_symbols": 256, "num_speakers": 1, "phoneme_id_map": ids,
        "inference": {"length_scale": 1, "noise_scale": 0.667, "noise_w": 0.8},
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    return PiperVoice.load(model, config_path, include_alignments=True)


def panel(title, number, font):
    image = Image.new("RGB", (540, 960), "#080f1e")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((29, 98, 511, 657), 17, "#f3e4c8", outline="#c8a878", width=2)
    draw.text((51, 127), f"CAPY BK   /   {number}", font=font(15), fill="#725539", anchor="lm")
    draw.text((490, 127), "DRAFT", font=font(13), fill="#725539", anchor="rm")
    draw.text((51, 182), title, font=font(38), fill=INK, anchor="ls")
    draw.line((51, 202, 489, 202), fill="#c8a878", width=2)
    return image


def machine_frame(image, progress, font):
    draw = ImageDraw.Draw(image)
    draw.ellipse((365, 234, 449, 318), fill="#f6d591")
    draw.polygon([(30, 562), (510, 403), (510, 629), (30, 629)], fill="#cb9668")
    draw.line((32, 562, 507, 404), fill=INK, width=5)
    for i in range(8):
        x = 54 + i * 55
        y = int(567 - (x - 32) / 3)
        draw.line((x, y, x + 14, y - 4), fill="#aa7751", width=3)

    sprite = Image.new("RGBA", (272, 220))
    d = ImageDraw.Draw(sprite)
    d.rounded_rectangle((36, 142, 207, 179), 17, "#675e55", outline=INK, width=4)
    for x in range(52, 187, 26):
        d.ellipse((x, 149, x + 21, 170), "#bbb3a4", outline=INK, width=3)
    d.rounded_rectangle((62, 110, 190, 147), 9, AMBER, outline=INK, width=4)
    d.polygon([(75, 114), (78, 72), (129, 72), (151, 114)], fill=AMBER, outline=INK, width=4)
    d.polygon([(87, 83), (122, 83), (136, 106), (87, 106)], fill="#94c7c4", outline=INK, width=3)
    elbow = (207, 68 + int(7 * math.sin(progress * math.tau)))
    bucket = (236, 124 + int(6 * math.sin(progress * math.tau)))
    joints = [(166, 118), elbow, bucket]
    d.line(joints, fill=INK, width=16, joint="curve")
    d.line(joints, fill=AMBER, width=10, joint="curve")
    bx, by = bucket
    d.polygon([(bx - 9, by), (bx + 13, by - 1), (bx + 20, by + 14), (bx - 4, by + 17)],
              fill="#675e55", outline=INK, width=3)
    sprite = sprite.rotate(18.4, resample=Image.Resampling.BICUBIC, center=(122, 179))
    x = 168 + round(progress * 144)
    y = round(563 - (x - 30) / 3)
    image.paste(sprite, (x - 122, y - 179), sprite)
    draw.text((270, 610), "ĐỘ NGHIÊNG TĂNG", font=font(18), fill=INK, anchor="mm")


def tank_frame(image, progress, font):
    draw = ImageDraw.Draw(image)
    cx, cy = 261, 422
    amount = min(progress * 1.5, 1.0)
    angle = math.radians(-22 * amount * amount * (3 - 2 * amount))
    co, si = math.cos(angle), math.sin(angle)

    def point(x, y):
        return round(cx + x * co - y * si), round(cy + x * si + y * co)

    tank = [point(x, y) for x, y in [(-164, -76), (164, -76), (164, 76), (-164, 76)]]
    draw.polygon(tank, fill="#fffcf1")
    mask = Image.new("L", image.size)
    ImageDraw.Draw(mask).polygon(tank, fill=255)
    # The plane passes through the center of this symmetric, half-full tank.
    # Its horizontal surface therefore cuts the same cross-sectional area at every tilt.
    image.paste("#7fc2be", (0, cy, image.width, image.height), mask.crop((0, cy, image.width, image.height)))
    draw.line(tank + [tank[0]], fill=INK, width=5, joint="curve")
    start, end = point(113, -62), point(113, 64)
    draw.line((start, end), fill="#9b482f", width=5)
    draw.ellipse((start[0] - 7, start[1] - 7, start[0] + 7, start[1] + 7), fill="#9b482f")
    draw.text((270, 588), "BÌNH GIẢ ĐỊNH · ĐẦY MỘT NỬA", font=font(17), fill=INK, anchor="mm")
    draw.text((270, 615), "Vạch đỏ là vị trí cảm biến", font=font(16), fill="#725539", anchor="mm")


def cutaway_frames(shot, font_path):
    def font(size):
        return ImageFont.truetype(str(font_path), size)

    scene = {"machine": machine_frame, "tank": tank_frame}[shot["visual"]]
    background = panel(shot["title"], shot["id"], font)
    count = shot["duration_frames"]
    for i in range(count):
        image = background.copy()
        scene(image, i / (count - 1), font)
        yield image.resize((1080, 1920), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--tokens", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    output = args.out.resolve()
    if output.exists():
        parser.error(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        scratch = Path(scratch)
        stage = scratch / "shots"
        stage.mkdir()
        voice = load_voice(args.model, args.tokens, manifest["voice"], scratch / "voice.json")
        dry_voice = scratch / "dry_voice.wav"
        voice_filters = ",".join([
            "highpass=f=80",
            "equalizer=f=210:t=q:w=0.8:g=-2",
            "equalizer=f=2800:t=q:w=0.9:g=2.5",
            "volume=1.15",
            "alimiter=limit=0.86:level=0:latency=1",
        ])
        for shot in manifest["shots"]:
            count = shot["duration_frames"]
            cues = synthesize(voice, shot["captions"], count / FPS, dry_voice, length_scale=1.05)
            subprocess.run([
                args.ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(dry_voice),
                "-af", voice_filters, "-c:a", "pcm_s16le", str(stage / shot["voice"]),
            ], check=True)
            if shot["visual"] in ("studio_open", "studio_close"):
                source = ROOT / shot["asset"]["source"]
                check_hash(source, shot["asset"]["sha256"])
                poses = OPEN_POSES if shot["visual"] == "studio_open" else CLOSE_POSES
                frames = studio_frames(source, args.font, cues, count, poses, shot["title"])
            else:
                frames = cutaway_frames(shot, args.font)
            encode_picture(args.ffmpeg, frames, stage / shot["video"])
        stage.rename(output)


if __name__ == "__main__":
    main()
