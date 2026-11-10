"""Render the approved Capy GIF as a Vietnamese dialogue shot, offline."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from piper import PiperVoice, SynthesisConfig


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "episodes/EP01/pilot.json"
VOICE_SHA = "ec7c89e2c85f4d1edc24b6120c18aaf1bda614f06b511567eb9c7c0de15e2dab"
CONFIG_SHA = "fafb9da1354ed4b77c31af228ed41fb41cd825c14cffa105454b25e6ae751ee0"
FPS = 30
SIZE = (1080, 1920)
# Frame, original pose index. The lifts land on the question and the realization.
POSES = [
    (0, 0), (8, 1), (17, 2), (27, 3), (41, 2), (55, 1), (68, 2),
    (79, 3), (88, 4), (94, 5), (101, 6), (109, 7),
    (111, 1), (119, 2), (130, 1), (144, 2), (158, 3), (170, 2),
    (180, 3), (187, 4), (193, 5), (200, 6), (207, 7),
]
# Coordinates measured on the exact GIF. x/y are the mouth's upper edge center.
# The last value is the original mouth depth.
MOUTHS = {
    1: (246, 156, 17), 2: (237, 147, 24), 3: (243, 135, 29),
    4: (246, 110, 27), 5: (240, 148, 26), 6: (240, 152, 24),
}


def check_hash(path, digest):
    with path.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != digest:
        raise ValueError(f"SHA-256 mismatch: {path}")


def mouth_shape(phoneme):
    if phoneme in "aɑæɐ":
        return 1.0, 1.06
    if phoneme in "oɔuʊw":
        return 0.63, 0.71
    if phoneme in "iɪeɛɜɤɯəʌy":
        return 0.49, 1.12
    if phoneme in "bmp":
        return 0.11, 0.95
    if phoneme.isalpha():
        return 0.35, 0.96
    return 0.13, 0.97


def synthesize(model, captions, duration, voice_path):
    voice = PiperVoice.load(model, include_alignments=True)
    config = SynthesisConfig(length_scale=1.20, noise_scale=0, noise_w_scale=0, volume=0.72)
    rate = voice.config.sample_rate
    audio = np.zeros(round(rate * duration), dtype="<i2")
    cues = []
    for caption in captions:
        start = round(caption["start_ms"] * rate / 1000)
        limit = round(caption["end_ms"] * rate / 1000)
        cursor = start
        line = caption["text"].replace("\n", " ")
        for chunk in voice.synthesize(line, config, include_alignments=True):
            if not chunk.phoneme_alignments:
                raise ValueError("Piper returned no phoneme alignment for the pilot.")
            samples = chunk.audio_int16_array
            end = cursor + len(samples)
            if end > limit:
                raise ValueError(f"Voice exceeds the caption window by {(end - limit) / rate:.3f}s: {line}")
            audio[cursor:end] = samples
            for phoneme in chunk.phoneme_alignments:
                next_sample = min(cursor + phoneme.num_samples, end)
                if next_sample > cursor:
                    cues.append((cursor / rate, next_sample / rate, *mouth_shape(phoneme.phoneme)))
                cursor = next_sample
            cursor = end
        print(f"{start / rate:.3f}–{cursor / rate:.3f}s  {line}")

    with wave.open(str(voice_path), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(audio.tobytes())
    return cues


def retime_mouth(frame, pose, opening, width):
    if pose not in MOUTHS:
        return frame
    x, y, depth = MOUTHS[pose]
    left, top, right, bottom = x - 24, y - 3, x + 25, y + depth + 11
    patch = np.asarray(frame.crop((left, top, right, bottom)))
    rows, columns = np.indices(patch.shape[:2], dtype=float)
    # Hold the top lip and patch edges in place. Scale the opening and blend
    # the displacement out through the surrounding muzzle.
    target_depth = 3 + (depth - 3) * opening
    old_rows = np.interp(rows, [0, 3, 3 + target_depth, bottom - top - 1],
                         [0, 3, 3 + depth, bottom - top - 1])
    edge_x = np.clip((24 - abs(columns - 24)) / 8, 0, 1)
    old_rows = rows + (old_rows - rows) * edge_x
    target_width = 15 * width
    old_columns = np.interp(columns, [0, 24 - target_width, 24, 24 + target_width, 48],
                            [0, 9, 24, 39, 48])
    edge_y = np.clip(np.minimum(rows, bottom - top - 1 - rows) / 6, 0, 1)
    old_columns = columns + (old_columns - columns) * edge_y

    iy, ix = old_rows.astype(int), old_columns.astype(int)
    fy, fx = (old_rows - iy)[..., None], (old_columns - ix)[..., None]
    below = np.minimum(iy + 1, patch.shape[0] - 1)
    rightward = np.minimum(ix + 1, patch.shape[1] - 1)
    upper = patch[iy, ix] * (1 - fx) + patch[iy, rightward] * fx
    lower = patch[below, ix] * (1 - fx) + patch[below, rightward] * fx
    result = frame.copy()
    result.paste(Image.fromarray((upper * (1 - fy) + lower * fy).astype(np.uint8)), (left, top))
    return result


def make_canvas(font_path):
    navy, light, cyan, gold = "#101d35", "#f2f7ff", "#76ddfc", "#ffd075"
    canvas = Image.new("RGB", SIZE, "#080f1e")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((58, 196, 1022, 1314), radius=30, fill=navy, outline="#294461", width=2)
    draw.line((94, 418, 986, 418), fill="#294461", width=2)
    draw.rounded_rectangle((93, 235, 268, 285), radius=15, fill="#20374f")
    def font(size):
        return ImageFont.truetype(str(font_path), size)
    draw.text((180, 259), "CAPY BK", font=font(29), fill=cyan, anchor="mm")
    draw.text((986, 261), "TẬP 01  /  DRAFT", font=font(26), fill=gold, anchor="rm")
    draw.text((94, 373), "DẦU ĐI ĐÂU?", font=font(76), fill=light, anchor="ls")
    draw.rounded_rectangle((94, 443, 144, 451), radius=4, fill=gold)
    draw.text((165, 448), "MÁY XÚC LÊN DỐC", font=font(28), fill=cyan, anchor="lm")
    return canvas


def render_picture(ffmpeg, source, font, cues, count, target):
    with Image.open(source) as gif:
        if gif.format != "GIF" or gif.size != (478, 354) or gif.n_frames != 9:
            raise ValueError("Pilot rig expects the approved 478×354 GIF with nine poses.")
        frames = []
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append(gif.convert("RGB"))
    canvas = make_canvas(font)
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-video_size", "1080x1920", "-framerate", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-threads", "4", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
    ]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as process:
        pose_index = 0
        for frame_number in range(count):
            while pose_index + 1 < len(POSES) and frame_number >= POSES[pose_index + 1][0]:
                pose_index += 1
            pose = POSES[pose_index][1]
            t = (frame_number + 0.5) / FPS
            # Average over one neighboring frame on each side to soften viseme changes.
            shapes = [
                next(((openness, width) for start, end, openness, width in cues if start <= sample < end),
                     (0.10, 0.97))
                for sample in (t - 1 / FPS, t, t + 1 / FPS)
            ]
            opening, width = ((prev + 2 * now + following) / 4 for prev, now, following in zip(*shapes))
            picture = retime_mouth(frames[pose], pose, opening, width)
            # The full studio plate stays inside the card at every camera position.
            scale = 1 + 0.018 * (1 - math.cos(math.tau * t / (count / FPS))) / 2
            w = round(916 * scale)
            h = round(w * picture.height / picture.width)
            frame = canvas.copy()
            frame.paste(picture.resize((w, h), Image.Resampling.LANCZOS), ((1080 - w) // 2, 851 - h // 2))
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError("FFmpeg failed to render the pilot picture.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    shot, = json.loads(PILOT.read_text(encoding="utf-8"))["shots"]
    source = ROOT / shot["asset"]["source"]
    check_hash(source, shot["asset"]["sha256"])
    check_hash(args.model, VOICE_SHA)
    check_hash(Path(str(args.model) + ".json"), CONFIG_SHA)
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Output already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as scratch:
        stage = Path(scratch) / "pilot"
        stage.mkdir()
        cues = synthesize(args.model, shot["captions"], shot["duration_frames"] / FPS, stage / shot["voice"])
        render_picture(args.ffmpeg, source, args.font, cues, shot["duration_frames"], stage / shot["video"])
        stage.rename(out)


if __name__ == "__main__":
    main()
