"""Smoke-test CapCut packaging with generated fixtures."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave


FFMPEG = os.getenv("CAPY_FFMPEG", "ffmpeg")
FFPROBE = os.getenv("CAPY_FFPROBE", "ffprobe")
BUILDER = Path(__file__).with_name("build_video.py")


class VideoPipelineTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.manifest = {
            "stage": "episode", "profile": "youtube", "shots": [],
        }
        for name, start, frames in (("S01", 0, 17), ("S02", 17, 22)):
            self.manifest["shots"].append({
                "id": name, "start_frame": start, "duration_frames": frames,
                "video": "picture.mp4", "voice": "voice.wav", "sfx": None,
                "asset": {
                    "source": "generated fixture", "date": "2026-11-10", "shot": name,
                    "method": "FFmpeg color and sine", "prompt": "smoke-test fixture",
                    "rights": "synthetic", "approval": "DRAFT",
                },
                "captions": [{"start_ms": 0, "end_ms": 500, "text": "Mức dầu"}],
            })

    def build(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        return subprocess.run([
            sys.executable, str(BUILDER), "--manifest", str(path),
            "--out", str(self.root / "handoff"), "--ffmpeg", FFMPEG, "--ffprobe", FFPROBE,
        ], capture_output=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})

    def test_missing_media_creates_no_handoff(self):
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing or invalid media path: picture.mp4", result.stderr)
        self.assertFalse((self.root / "handoff").exists())

    def test_landscape_concatenation_and_sfx(self):
        subprocess.run([
            FFMPEG, "-v", "error", "-f", "lavfi", "-i", "color=c=navy:s=960x540:r=30",
            "-frames:v", "30", "-c:v", "libx264", str(self.root / "picture.mp4"),
        ], check=True)
        subprocess.run([
            FFMPEG, "-v", "error", "-f", "lavfi", "-i", "sine=f=500:d=0.5",
            "-c:a", "pcm_s16le", str(self.root / "voice.wav"),
        ], check=True)
        self.manifest["shots"][1]["sfx"] = "voice.wav"
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("39 frames", result.stdout)
        handoff = self.root / "handoff"
        self.assertTrue((handoff / "DRAFT_preview.mp4").is_file())
        with wave.open(str(handoff / "audio/S02_sfx.wav"), "rb") as sfx:
            self.assertEqual((sfx.getframerate(), sfx.getnframes()), (48000, 35200))
        subtitles = (handoff / "captions_vi.srt").read_text(encoding="utf-8")
        self.assertIn("00:00:00,567 --> 00:00:01,067\nMức dầu", subtitles)


if __name__ == "__main__":
    unittest.main()
