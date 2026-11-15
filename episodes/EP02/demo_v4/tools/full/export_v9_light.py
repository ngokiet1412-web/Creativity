"""Make a compact MP4 and three smaller copies for offline review."""
import argparse
import os
from pathlib import Path
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--nvenc", action="store_true")
    args = ap.parse_args()
    folder = args.folder.resolve()
    ffmpeg = os.environ.get("FFMPEG", "ffmpeg")

    def run(*options):
        subprocess.run([ffmpeg, "-v", "error", "-y", *options], cwd=folder, check=True)

    # Roughly 39 MB for ten minutes. Use AAC-LC in stereo and mark it default.
    light = "EP02_V9_nhe_co_tieng.mp4"
    software = ["-c:v", "libx264", "-preset", "fast", "-b:v", "425k", "-maxrate", "460k", "-bufsize", "900k"]
    hardware = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "cbr", "-multipass", "qres",
                "-b:v", "425k", "-maxrate", "425k", "-bufsize", "850k"]
    run("-i", "EP02_FULL_V9_VOICED_DRAFT.mp4",
        "-vf", "ass=EP02_FULL_V9_vi.ass,scale=960:540:flags=lanczos",
        "-map", "0:v:0", "-map", "0:a:0", *(hardware if args.nvenc else software),
        "-g", "60", "-force_key_frames", "198,396", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-profile:a", "aac_low", "-b:a", "88k", "-ar", "48000", "-ac", "2",
        "-disposition:a:0", "default", "-movflags", "+faststart", light)
    run("-i", light, "-map", "0:v:0", "-map", "0:a:0", "-c", "copy",
        "-f", "segment", "-segment_times", "198,396", "-segment_start_number", "1",
        "-reset_timestamps", "1", "-segment_format_options", "movflags=+faststart",
        "EP02_V9_phan_%d.mp4")

    # Intro test is independently playable in a phone player or audio app.
    run("-i", light, "-t", "31", "-map", "0:v:0", "-map", "0:a:0",
        "-c", "copy", "-movflags", "+faststart", "EP02_V9_mo_dau.mp4")
    run("-i", "EP02_V9_mo_dau.mp4", "-vn", "-c:a", "libmp3lame",
        "-b:a", "96k", "EP02_V9_nghe_thu.mp3")


if __name__ == "__main__":
    main()
