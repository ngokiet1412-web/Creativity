"""Smoke tests for the CAB-01 technical pipeline using synthetic fixtures."""

import json
import os
from pathlib import Path
import tempfile
import unittest

import cab01


FF = os.getenv("CAPY_FFMPEG", "ffmpeg")
FP = os.getenv("CAPY_FFPROBE", "ffprobe")
CONFIG = json.loads((cab01.SHOT_DIR / "shot.json").read_text(encoding="utf-8"))
CAPTIONS = cab01.SHOT_DIR / "CAB-01_vi_v01.srt"


class Cab01Test(unittest.TestCase):
    def test_approved_assets(self):
        self.assertEqual(set(cab01.verify_assets()), {"CAPY-MASTER", "R01", "R02", "R03"})

    def test_captions_match_line_and_fit_shot(self):
        cab01.check_subtitles(CAPTIONS, 7.5, CONFIG["dialogue"])
        with self.assertRaisesRegex(ValueError, "outside the shot"):
            cab01.check_subtitles(CAPTIONS, 5.5, CONFIG["dialogue"])
        with self.assertRaisesRegex(ValueError, "approved Vietnamese line"):
            cab01.check_subtitles(CAPTIONS, 7.5, "An unrelated line.")

    def test_review_from_motion_and_voice(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            motion, voice, output = root / "motion.mp4", root / "voice.wav", root / "review.mp4"
            cab01.ffmpeg(FF, "-v", "error", "-f", "lavfi", "-i", "color=c=navy:s=360x640:r=30:d=7.5",
                         "-c:v", "libx264", motion)
            cab01.ffmpeg(FF, "-v", "error", "-f", "lavfi", "-i", "sine=f=420:r=48000:d=7.5",
                         "-c:a", "pcm_s16le", voice)
            with self.assertRaises(FileNotFoundError):
                cab01.check_subtitles(root / "missing.srt", 7.5, CONFIG["dialogue"])
            cab01.review(motion, voice, CAPTIONS, output, CONFIG, FF, FP)
            self.assertTrue(output.is_file())
            silent = root / "silence.wav"
            cab01.ffmpeg(FF, "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                         "-t", "7.5", "-c:a", "pcm_s16le", silent)
            with self.assertRaisesRegex(ValueError, "silent"):
                cab01.verify_render(output, silent, CAPTIONS, CONFIG, FF, FP)


if __name__ == "__main__":
    unittest.main()
