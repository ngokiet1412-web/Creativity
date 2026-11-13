"""Verify CAB-01 assets, prepare the CapCut handoff and check real returned takes."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SHOT_DIR = ROOT / "episodes/EP01/shots/CAB-01"
LEDGER = ROOT / "assets/APPROVED_SHA256_V2.json"
TIMECODE = r"(\d{2}):([0-5]\d):([0-5]\d),(\d{3})"
TIME_RANGE = re.compile(TIMECODE + r" --> " + TIMECODE)


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def verify_assets():
    paths = {}
    for asset in json.loads(LEDGER.read_text(encoding="utf-8")):
        path = ROOT / asset["path"]
        if path.stat().st_size != asset["bytes"] or digest(path) != asset["sha256"]:
            raise ValueError(f"Approved bytes do not match: {asset['id']} ({path.name})")
        with path.open("rb") as file:
            header = file.read(24)
        if asset["format"] == "GIF89a" and header[:6] == b"GIF89a":
            width, height = struct.unpack("<HH", header[6:10])
        elif asset["format"] == "PNG" and header[:16] == b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
            width, height = struct.unpack(">II", header[16:24])
        else:
            raise ValueError(f"Wrong image signature: {path.name}")
        if (width, height) != (asset["width"], asset["height"]):
            raise ValueError(f"Wrong image dimensions: {path.name}")
        paths[asset["id"]] = path
        print(f"{asset['id']} {width}×{height} {asset['sha256']}")
    return paths


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")


def ffmpeg(binary, *args):
    return run(binary, "-nostdin", "-hide_banner", *args)


def streams(ffprobe, path, count=False):
    flags = ["-count_frames"] if count else []
    return json.loads(run(ffprobe, "-v", "error", *flags, "-show_streams", "-of", "json", path).stdout)["streams"]


def single_stream(media, kind):
    found = [stream for stream in media if stream["codec_type"] == kind]
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} stream, found {len(found)}.")
    return found[0]


def require_duration(seconds, config):
    if not config["min_frames"] / config["fps"] <= seconds <= config["max_frames"] / config["fps"]:
        raise ValueError(f"CAB-01 must last 6–8 seconds. Found {seconds:.3f}s.")


def subtitle_ms(parts):
    hours, minutes, seconds, ms = (int(part) for part in parts)
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + ms


def check_subtitles(path, seconds, dialogue):
    blocks = re.split(r"\n[ \t]*\n", path.read_text(encoding="utf-8-sig").strip())
    previous_end = 0
    words = []
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        match = TIME_RANGE.fullmatch(lines[1]) if len(lines) >= 3 else None
        if not match or lines[0] != str(index) or not all(line.strip() for line in lines[2:]):
            raise ValueError(f"Invalid UTF-8 SRT cue {index}: {path.name}")
        start, end = (subtitle_ms(match.groups()[i:i + 4]) for i in (0, 4))
        if not previous_end <= start < end <= round(seconds * 1000):
            raise ValueError(f"Cue {index} overlaps or falls outside the shot: {path.name}")
        previous_end = end
        words.extend(" ".join(lines[2:]).split())
    if " ".join(words) != dialogue:
        raise ValueError("Subtitles must match the approved Vietnamese line.")


def check_voice(ffprobe, path, config, seconds, exact_pcm=True):
    audio = single_stream(streams(ffprobe, path), "audio")
    if exact_pcm and (
        path.suffix.lower() != ".wav"
        or audio["codec_name"] not in ("pcm_s16le", "pcm_s24le")
        or int(audio["sample_rate"]) != config["audio_sample_rate"]
        or audio["channels"] not in (1, 2)
    ):
        raise ValueError("Voice must be mono or stereo PCM WAV at 48 kHz, 16- or 24-bit.")
    if abs(float(audio["duration"]) - seconds) > 1 / config["fps"]:
        raise ValueError("Voice WAV must start at timeline zero and span the full shot.")


def audio_levels(binary, path):
    result = ffmpeg(binary, "-i", path, "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-")
    mean = re.search(r"mean_volume: (-?[\d.]+) dB", result.stderr)
    peak = re.search(r"max_volume: (-?[\d.]+) dB", result.stderr)
    if not mean or not peak or float(peak[1]) < -45:
        raise ValueError(f"Audio appears silent or too quiet: {path.name}")
    if float(peak[1]) >= 0:
        raise ValueError(f"Audio reaches digital full scale: {path.name}")
    return float(mean[1]), float(peak[1])


def prepare(guide, output, config, ff, fp, style_still=None):
    paths = verify_assets()
    seconds = config["target_frames"] / config["fps"]
    check_voice(fp, guide, config, seconds, exact_pcm=False)
    sid, version = config["id"], config["version"]
    captions = SHOT_DIR / f"{sid}_vi_{version}.srt"
    check_subtitles(captions, seconds, config["dialogue"])
    output = output.resolve()
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        stage = Path(scratch) / "handoff"
        for name in ("references", "audio", "subtitles", "returns"):
            (stage / name).mkdir(parents=True)
        for ref in ("R01", "R02", config["reference"]):
            shutil.copyfile(paths[ref], stage / "references" / paths[ref].name)
        if style_still is not None:
            candidate = config["style"]["style_candidate"]
            if digest(style_still) != candidate["sha256"]:
                raise ValueError("Style still does not match the CAB-01 draft fingerprint.")
            (stage / "style_candidate").mkdir()
            shutil.copyfile(style_still, stage / "style_candidate" / candidate["file"])
        for name in ("shot.json", f"{sid}_prompt_{version}.txt", f"{sid}_qa_{version}.md"):
            shutil.copyfile(SHOT_DIR / name, stage / name)
        shutil.copyfile(SHOT_DIR / "README.md", stage / "READ_ME.md")
        shutil.copyfile(captions, stage / "subtitles" / captions.name)

        wav = stage / "audio" / f"{sid}_guide_vi_{version}.wav"
        rate = config["audio_sample_rate"]
        length = round(seconds * rate)
        ffmpeg(ff, "-v", "error", "-i", guide, "-map", "0:a:0", "-map_metadata", "-1",
               "-af", f"aresample={rate},highpass=f=75,apad=whole_len={length},atrim=end_sample={length}",
               "-ac", "1", "-c:a", "pcm_s16le", wav)
        check_voice(fp, wav, config, seconds)
        _, peak = audio_levels(ff, wav)
        files = sorted(path for path in stage.rglob("*") if path.is_file())
        (stage / "SHA256SUMS.txt").write_text(
            "".join(f"{digest(path)}  {path.relative_to(stage).as_posix()}\n" for path in files), encoding="utf-8",
        )
        stage.rename(output)
    print(f"Prepared {output} | {seconds:.2f}s timing WAV, 48 kHz, peak {peak:.1f} dBFS")


def verify_render(clip, voice, captions, config, ff, fp):
    media = streams(fp, clip, count=True)
    video = single_stream(media, "video")
    audio = single_stream(media, "audio")
    fps = config["fps"]
    frames = int(video["nb_read_frames"])
    seconds = frames / fps
    require_duration(seconds, config)
    if (
        clip.suffix.lower() != ".mp4"
        or video["codec_name"] != "h264"
        or (video["width"], video["height"]) != (config["width"], config["height"])
        or Fraction(video["avg_frame_rate"]) != fps
        or Fraction(video["r_frame_rate"]) != fps
        or abs(float(video["duration"]) - seconds) > 1 / fps
        or video.get("sample_aspect_ratio", "1:1") not in ("1:1", "N/A")
    ):
        raise ValueError("Render must be 1080×1920 H.264 MP4 at 30 fps with square pixels.")
    pts = json.loads(run(
        fp, "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", clip,
    ).stdout)["frames"]
    times = [float(frame["best_effort_timestamp_time"]) for frame in pts]
    if len(times) != frames or any(abs(b - a - 1 / fps) > 0.001 for a, b in zip(times, times[1:])):
        raise ValueError("Video frame timestamps must maintain 30 fps cadence.")
    if audio["codec_name"] != "aac" or int(audio["sample_rate"]) != config["audio_sample_rate"]:
        raise ValueError("Render audio must be AAC at 48 kHz.")
    if (
        abs(float(video.get("start_time", 0))) > 1 / fps
        or abs(float(audio.get("start_time", 0))) > 1 / fps
        or abs(float(audio["duration"]) - seconds) > 1 / fps
    ):
        raise ValueError("Audio and video timeline starts and lengths must match within one frame.")
    check_voice(fp, voice, config, seconds)
    check_subtitles(captions, seconds, config["dialogue"])
    _, peak = audio_levels(ff, clip)
    audio_levels(ff, voice)
    ffmpeg(ff, "-v", "error", "-xerror", "-i", clip, "-f", "null", "-")
    print(f"Technical pass: {frames} frames, {seconds:.3f}s, H.264 / AAC 48 kHz, peak {peak:.1f} dBFS.")
    print("Human review: acting, machinery, BK logo, dialogue/lip-sync and caption placement.")


def review(motion, voice, captions, output, config, ff, fp):
    if output.exists() or output.suffix.lower() != ".mp4":
        raise ValueError("Choose a new .mp4 output for the review render.")
    video = single_stream(streams(fp, motion), "video")
    width, height, fps = config["width"], config["height"], config["fps"]
    if video["width"] * height != video["height"] * width:
        raise ValueError("Source motion must be composed at 9:16.")
    seconds = round(float(video["duration"]) * fps) / fps
    require_duration(seconds, config)
    check_voice(fp, voice, config, seconds)
    check_subtitles(captions, seconds, config["dialogue"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        result = Path(scratch) / "review.mp4"
        rate = config["audio_sample_rate"]
        length = round(seconds * rate)
        ffmpeg(ff, "-v", "error", "-i", motion, "-i", voice,
               "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "-1",
               "-vf", f"fps={fps},scale={width}:{height}:flags=lanczos,setsar=1",
               "-af", f"apad=whole_len={length},atrim=end_sample={length}", "-t", f"{seconds:.6f}",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", str(rate),
               "-movflags", "+faststart", result)
        verify_render(result, voice, captions, config, ff, fp)
        result.rename(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify-assets")
    prep = commands.add_parser("prepare", help="Prepare the local CapCut input folder.")
    prep.add_argument("--guide-wav", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    prep.add_argument("--style-still", type=Path, help="Include the pinned 2D draft alongside the approved references.")
    validate = commands.add_parser("validate", help="Check a completed CapCut return.")
    validate.add_argument("--take", type=Path, required=True)
    validate.add_argument("--version", default="v01")
    render = commands.add_parser("review", help="Mux a real CapCut motion clip and timed voice stem.")
    for option in ("motion", "voice", "captions", "out"):
        render.add_argument(f"--{option}", type=Path, required=True)
    args = parser.parse_args()

    try:
        if args.command == "verify-assets":
            verify_assets()
            return
        ff, fp = (shutil.which(path) for path in (args.ffmpeg, args.ffprobe))
        if not ff or not fp:
            raise ValueError("FFmpeg and ffprobe are required.")
        config = json.loads((SHOT_DIR / "shot.json").read_text(encoding="utf-8"))
        if args.command == "prepare":
            prepare(args.guide_wav, args.out, config, ff, fp, args.style_still)
        elif args.command == "review":
            review(args.motion, args.voice, args.captions, args.out, config, ff, fp)
        else:
            version = args.version
            if not re.fullmatch(r"v[0-9]{2}", version):
                raise ValueError("Use version vNN, for example v01.")
            sid = config["id"]
            for name in (f"{sid}_prompt_{version}.txt", f"{sid}_qa_{version}.md"):
                if not (args.take / name).read_text(encoding="utf-8-sig").strip():
                    raise ValueError(f"Empty return note: {name}")
            verify_render(args.take / f"{sid}_{version}.mp4", args.take / f"{sid}_voice_{version}.wav",
                          args.take / f"{sid}_vi_{version}.srt", config, ff, fp)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"{error.stderr.strip() or error}\n")
    except (KeyError, OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
