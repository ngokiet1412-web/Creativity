"""Export the 1080p review master, its 1080p parts, and a short studio preview."""
import argparse
import os
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--nvenc", action="store_true", help="use a verified NVIDIA encoder")
    args = parser.parse_args()
    ffmpeg = os.environ.get("FFMPEG", "ffmpeg")

    def run(*options):
        subprocess.run([ffmpeg, "-v", "error", "-y", *options], check=True, cwd=args.folder)

    parts = "100,200,300,400,500"
    output = "EP02_V10_1080p_DRAFT.mp4"
    software = ["-c:v", "libx264", "-preset", "fast", "-crf", "19", "-maxrate", "2400k", "-bufsize", "4800k"]
    hardware = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-multipass", "qres",
                "-b:v", "2100k", "-maxrate", "2400k", "-bufsize", "4800k"]
    run("-i", "EP02_FULL_V10_VOICED_DRAFT.mp4", "-vf", "ass=EP02_FULL_V10_vi.ass",
        "-map", "0:v:0", "-map", "0:a:0", *(hardware if args.nvenc else software),
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", "60", "-force_key_frames", parts,
        "-c:a", "aac", "-profile:a", "aac_low", "-b:a", "112k", "-ar", "48000", "-ac", "2",
        "-disposition:a:0", "default", "-movflags", "+faststart", output)
    run("-i", output, "-map", "0:v:0", "-map", "0:a:0", "-c", "copy",
        "-f", "segment", "-segment_times", parts, "-segment_start_number", "1",
        "-reset_timestamps", "1", "-segment_format_options", "movflags=+faststart",
        "EP02_V10_HD_phan_%d.mp4")
    run("-i", output, "-t", "30", "-map", "0:v:0", "-map", "0:a:0", "-c", "copy",
        "-movflags", "+faststart", "EP02_V10_studio_1080p.mp4")


if __name__ == "__main__":
    main()
