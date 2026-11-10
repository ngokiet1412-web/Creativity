"""Package ordered shots and render an MP4 review copy for CapCut Desktop."""

import argparse
import csv
from fractions import Fraction
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import wave


FPS = 30
RATE = 48_000
PROFILES = {"tiktok": (1080, 1920), "youtube": (1920, 1080)}
ENCODE_VIDEO = [
    "-c:v", "libx264", "-threads", "4", "-preset", "fast", "-crf", "17",
    "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
]


def run(*command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)


def ffmpeg(binary, cwd, *options):
    run(binary, "-nostdin", "-hide_banner", "-loglevel", "error", *options, cwd=cwd)


def probe(binary, path, count_frames=False):
    options = ["-count_frames"] if count_frames else []
    return json.loads(subprocess.check_output([
        binary, "-v", "error", *options, "-show_streams", "-of", "json", str(path),
    ]))["streams"]


def media_file(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Missing or invalid media path: {name}")
    return path


def read_manifest(path, media):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    width, height = PROFILES[manifest["profile"]]
    shots = manifest["shots"]
    if not shots or manifest["stage"] not in ("pilot", "episode"):
        raise ValueError("Supply shots and a stage of pilot or episode.")
    cursor = 0
    ids = set()
    for shot in shots:
        name, start, count = shot["id"], shot["start_frame"], shot["duration_frames"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name) or name.casefold() in ids:
            raise ValueError(f"Invalid or duplicate shot ID: {name}")
        ids.add(name.casefold())
        if type(start) is not int or start != cursor or type(count) is not int or count <= 0:
            raise ValueError(f"Shots must be contiguous and have positive integer frame counts: {name}")
        cursor += count
        for field in ("source", "date", "shot", "method", "prompt", "rights", "approval"):
            if not shot["asset"].get(field):
                raise ValueError(f"Missing asset provenance field {field}: {name}")
        for kind in ("video", "voice", "sfx"):
            if kind != "sfx" or shot.get(kind):
                shot[kind] = media_file(media, shot[kind])
        last_end = 0
        for cue in shot["captions"]:
            cue_start, cue_end = cue["start_ms"], cue["end_ms"]
            if (
                type(cue_start) is not int or type(cue_end) is not int
                or not last_end <= cue_start < cue_end <= count * 1000 / FPS
                or not cue["text"].strip() or "\n\n" in cue["text"]
            ):
                raise ValueError(f"Invalid or overlapping captions: {name}")
            last_end = cue_end
    if manifest["stage"] == "pilot" and not 6 * FPS <= cursor <= 8 * FPS:
        raise ValueError("Pilot must run for 6–8 seconds.")
    return (width, height), shots, cursor


def timestamp(ms):
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def prepare_shot(stage, shot, size, ff, fp):
    name = shot["id"]
    frames = shot["duration_frames"]
    width, height = size
    source = next((stream for stream in probe(fp, shot["video"]) if stream["codec_type"] == "video"), None)
    if source is None or source["width"] * height != source["height"] * width:
        raise ValueError(f"{name} needs a picture composed for {width}×{height}.")
    picture = f"clips/{name}_picture.mp4"
    ffmpeg(ff, stage, "-i", shot["video"], "-map", "0:v:0", "-map_metadata", "-1", "-an",
           "-vf", f"fps={FPS},scale={width}:{height}:flags=lanczos,setsar=1",
           "-frames:v", str(frames), *ENCODE_VIDEO, "-movflags", "+faststart", picture)
    video, = probe(fp, stage / picture)
    if int(video["nb_frames"]) != frames:
        raise ValueError(f"Source picture is shorter than the shot: {name}")

    audio = {}
    samples = frames * (RATE // FPS)
    for kind in ("voice", "sfx"):
        if not shot.get(kind):
            continue
        stem = f"audio/{name}_{kind}.wav"
        ffmpeg(ff, stage, "-i", shot[kind], "-map", "0:a:0", "-map_metadata", "-1", "-vn",
               "-af", f"aresample={RATE},apad,atrim=end_sample={samples}",
               "-ac", "1", "-c:a", "pcm_s16le", stem)
        with wave.open(str(stage / stem), "rb") as result:
            if result.getnframes() != samples or result.getframerate() != RATE:
                raise ValueError(f"Unexpected stem duration or sample rate: {stem}")
        audio[kind] = stem
    return picture, audio


def write_stem(stage, path, shots, tracks, kind):
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        for shot, stems in zip(shots, tracks):
            samples = shot["duration_frames"] * (RATE // FPS)
            if kind in stems:
                with wave.open(str(stage / stems[kind]), "rb") as source:
                    for remaining in range(samples, 0, -RATE):
                        output.writeframesraw(source.readframes(min(remaining, RATE)))
            else:
                for remaining in range(samples, 0, -RATE):
                    output.writeframesraw(bytes(2 * min(remaining, RATE)))


def package(stage, scratch, shots, size, count, ff, fp):
    (stage / "clips").mkdir()
    (stage / "audio").mkdir()
    pictures, tracks, subtitles = [], [], []
    with (stage / "shot_table.csv").open("w", encoding="utf-8-sig", newline="") as table:
        writer = csv.writer(table)
        writer.writerow(["shot_id", "start_frame", "duration_frames", "picture", "voice", "sfx", "status"])
        for shot in shots:
            picture, audio = prepare_shot(stage, shot, size, ff, fp)
            pictures.append(picture)
            tracks.append(audio)
            start = shot["start_frame"]
            writer.writerow([shot["id"], start, shot["duration_frames"], picture,
                             audio["voice"], audio.get("sfx", ""), shot["asset"]["approval"]])
            offset = round(start * 1000 / FPS)
            for cue in shot["captions"]:
                begin, end = (timestamp(offset + cue[key]) for key in ("start_ms", "end_ms"))
                subtitles.append(f"{len(subtitles) + 1}\n{begin} --> {end}\n{cue['text']}\n")
    captions = stage / "captions_vi.srt"
    captions.write_text("\n".join(subtitles), encoding="utf-8")

    concat = scratch / "shots.ffconcat"
    concat.write_text("".join(f"file 'handoff/{picture}'\n" for picture in pictures), encoding="ascii")
    voice = scratch / "voice.wav"
    write_stem(stage, voice, shots, tracks, "voice")
    audio = ["-i", voice]
    if any("sfx" in stems for stems in tracks):
        sfx = scratch / "sfx.wav"
        write_stem(stage, sfx, shots, tracks, "sfx")
        audio += ["-i", sfx, "-filter_complex", "[1:a][2:a]amix=weights='1 0.4':normalize=0,alimiter=limit=0.95:level=0:latency=1[dialogue]",
                  "-map", "[dialogue]"]
    else:
        audio += ["-map", "1:a:0"]

    preview = stage / "DRAFT_preview.mp4"
    # Each prepared clip has exactly its manifest frame count. Reset the
    # concatenated timestamps so MP4 container rounding cannot accumulate.
    filters = [f"settb=1/{FPS}", "setpts=N"]
    if subtitles:
        margin = 70 if size[1] > size[0] else 45
        style = f"FontName=Arial,FontSize=13,Bold=1,Outline=2,Shadow=0,MarginV={margin},MarginL=30,MarginR=30"
        filters.append(f"subtitles=captions_vi.srt:force_style='{style}'")
    ffmpeg(ff, stage, "-f", "concat", "-safe", "0", "-i", concat, *audio, "-map", "0:v:0",
           "-map_metadata", "-1", "-vf", ",".join(filters), "-r", str(FPS), "-fps_mode", "cfr",
           *ENCODE_VIDEO, "-c:a", "aac", "-b:a", "160k",
           "-ar", str(RATE), "-movflags", "+faststart", preview)
    verify_preview(ff, fp, stage, preview, size, count)


def verify_preview(ff, fp, stage, preview, size, count):
    streams = probe(fp, preview, count_frames=True)
    video, = (s for s in streams if s["codec_type"] == "video")
    audio, = (s for s in streams if s["codec_type"] == "audio")
    duration = count / FPS
    if (
        (video["width"], video["height"]) != size or video["codec_name"] != "h264"
        or Fraction(video["avg_frame_rate"]) != FPS or int(video["nb_read_frames"]) != count
        or abs(float(video["duration"]) - duration) > 1 / FPS
        or audio["codec_name"] != "aac" or int(audio["sample_rate"]) != RATE
        or abs(float(audio["duration"]) - duration) > 1 / FPS
    ):
        raise ValueError(
            f"Expected {size[0]}×{size[1]} H.264, {count} frames at {FPS} fps and AAC {RATE} Hz. "
            f"Got {video['width']}×{video['height']} {video['codec_name']}, "
            f"{video['nb_read_frames']} frames at {video['avg_frame_rate']}, "
            f"{audio['codec_name']} {audio['sample_rate']} Hz, "
            f"picture {video['duration']}s and sound {audio['duration']}s."
        )
    ffmpeg(ff, stage, "-xerror", "-i", preview, "-f", "null", "-")
    print(f"Verified {size[0]}×{size[1]}, {count} frames at {FPS} fps, {duration:.2f}s, H.264 / AAC 48 kHz")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--media-dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    media = (args.media_dir or args.manifest.parent).resolve()
    output = args.out.resolve()
    if output.exists():
        parser.error(f"Output already exists: {output}")
    ff, fp = (shutil.which(binary) for binary in (args.ffmpeg, args.ffprobe))
    if not ff or not fp:
        parser.error("FFmpeg and ffprobe are required.")
    try:
        size, shots, count = read_manifest(args.manifest, media)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
            stage = Path(scratch) / "handoff"
            stage.mkdir()
            package(stage, Path(scratch), shots, size, count, ff, fp)
            stage.rename(output)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
