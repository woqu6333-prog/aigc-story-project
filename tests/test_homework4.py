from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_video import create_video_plan


class Homework4VideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = PROJECT_ROOT / "outputs" / "video" / "homework4"
        cls.plan = json.loads(
            (cls.output_dir / "video-plan.json").read_text(encoding="utf-8")
        )

    def test_plan_reuses_homework3_timeline(self) -> None:
        generated = create_video_plan(
            PROJECT_ROOT / "outputs" / "audio" / "homework3" / "timeline.json"
        )
        self.assertEqual(len(generated["sections"]), 7)
        self.assertGreater(generated["duration_seconds"], 60)
        self.assertEqual([item["id"] for item in generated["sections"]], [1, 3, 7, 8, 17, 22, 30])
        self.assertGreaterEqual(len(generated["subtitles"]), 35)

    def test_video_meets_duration_requirement(self) -> None:
        from mutagen.mp4 import MP4

        video = self.output_dir / "xiaoyu-story-video.mp4"
        self.assertTrue(video.is_file())
        self.assertGreater(video.stat().st_size, 10_000_000)
        self.assertGreaterEqual(MP4(video).info.length, 60)

    def test_plan_records_required_media_details(self) -> None:
        self.assertEqual(self.plan["resolution"], "1280x720")
        self.assertEqual(self.plan["fps"], 24)
        self.assertEqual(self.plan["video_encoder"], "h264_nvenc")
        self.assertGreaterEqual(len(self.plan["subtitles"]), 35)
        roles = {item["role"] for item in self.plan["sections"]}
        self.assertGreaterEqual(len(roles), 3)

    def test_thumbnail_and_webpage_exist(self) -> None:
        self.assertGreater((self.output_dir / "thumbnail.jpg").stat().st_size, 50_000)
        source = PROJECT_ROOT / "src" / "video_web"
        html = (source / "index.html").read_text(encoding="utf-8")
        self.assertIn("<video controls", html)
        self.assertIn("assets/video/xiaoyu-story-video.mp4", html)
        self.assertNotRegex(html, r'(?:src|href)="https?://')

    def test_distribution_is_built(self) -> None:
        dist = PROJECT_ROOT / "dist" / "video"
        required = [
            dist / "index.html",
            dist / "assets" / "style.css",
            dist / "assets" / "thumbnail.jpg",
            dist / "assets" / "video" / "xiaoyu-story-video.mp4",
            dist / "data" / "video-plan.json",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"构建产物缺少：{path}")


if __name__ == "__main__":
    unittest.main()
