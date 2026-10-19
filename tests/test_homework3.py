from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from audiobook.builder import EMOTION_ADJUSTMENTS, load_script, segment_voice_settings


class Homework3AudiobookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.script_path = (
            PROJECT_ROOT / "outputs" / "stories" / "homework3-audiobook-script.json"
        )
        cls.audio_dir = PROJECT_ROOT / "outputs" / "audio" / "homework3"
        cls.script = load_script(cls.script_path)
        cls.timeline = json.loads(
            (cls.audio_dir / "timeline.json").read_text(encoding="utf-8")
        )

    def test_script_has_four_distinct_voices(self) -> None:
        roles = {segment["role"] for segment in self.script["segments"]}
        voices = {self.script["voices"][role]["voice"] for role in roles}
        self.assertEqual(len(roles), 4)
        self.assertEqual(len(voices), 4)

    def test_every_segment_has_supported_emotion_and_chapter(self) -> None:
        self.assertEqual(len(self.script["segments"]), 30)
        for segment in self.script["segments"]:
            with self.subTest(segment=segment["id"]):
                self.assertIn(segment["emotion"], EMOTION_ADJUSTMENTS)
                self.assertTrue(segment["chapter"])
                self.assertGreaterEqual(segment["pause_ms"], 500)

    def test_emotion_changes_voice_parameters(self) -> None:
        voice = self.script["voices"]["小雨"]
        curious = segment_voice_settings(voice, "好奇")
        whisper = segment_voice_settings(voice, "低语")
        self.assertEqual(curious["pitch"], "+11Hz")
        self.assertEqual(whisper["volume"], "-9%")
        self.assertNotEqual(curious["rate"], whisper["rate"])

    def test_final_audio_meets_three_minute_requirement(self) -> None:
        from mutagen.mp3 import MP3

        audio_path = self.audio_dir / "audiobook.mp3"
        self.assertTrue(audio_path.is_file())
        self.assertGreater(audio_path.stat().st_size, 5_000_000)
        self.assertGreaterEqual(MP3(audio_path).info.length, 180)

    def test_timeline_is_ordered_and_matches_audio(self) -> None:
        from mutagen.mp3 import MP3

        segments = self.timeline["segments"]
        self.assertEqual(len(segments), 30)
        self.assertEqual(self.timeline["voice_count"], 4)
        for previous, current in zip(segments, segments[1:]):
            self.assertLess(previous["start"], previous["end"])
            self.assertLessEqual(previous["end"], current["start"])
        audio_duration = MP3(self.audio_dir / "audiobook.mp3").info.length
        self.assertLess(abs(audio_duration - self.timeline["duration_seconds"]), 0.1)
        self.assertLess(audio_duration - segments[-1]["end"], 1.5)

    def test_synchronized_webpage_is_complete(self) -> None:
        source_dir = PROJECT_ROOT / "src" / "audiobook_web"
        html = (source_dir / "index.html").read_text(encoding="utf-8")
        script = (source_dir / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="audioPlayer"', html)
        self.assertIn('id="transcript"', html)
        self.assertIn("assets/audio/audiobook.mp3", html)
        self.assertIn('fetch("assets/audio/timeline.json")', script)
        self.assertIn("scrollIntoView", script)
        self.assertNotRegex(html, r'(?:src|href)="https?://')

    def test_distribution_is_built(self) -> None:
        dist = PROJECT_ROOT / "dist" / "audiobook"
        required = [
            dist / "index.html",
            dist / "assets" / "style.css",
            dist / "assets" / "app.js",
            dist / "assets" / "audio" / "audiobook.mp3",
            dist / "assets" / "audio" / "timeline.json",
            dist / "data" / "script.json",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"构建产物缺少：{path}")


if __name__ == "__main__":
    unittest.main()
