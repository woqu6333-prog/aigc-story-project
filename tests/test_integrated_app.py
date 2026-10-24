from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_app import story_request_from_payload


class IntegratedStoryAppTests(unittest.TestCase):
    def test_web_payload_maps_to_homework1_model(self) -> None:
        request = story_request_from_payload(
            {
                "name": "小雨",
                "age": 7,
                "interest": "恐龙",
                "setting": "月光森林",
                "theme": "courage",
                "story_length": "短篇",
                "target_age": 7,
                "plot_idea": "小雨在森林里发现脚印并帮助迷路的小鸟",
            }
        )
        self.assertEqual(request.hero_name, "小雨")
        self.assertEqual(request.theme, "勇气")
        self.assertEqual(request.setting, "月光森林")
        self.assertIn("帮助迷路的小鸟", request.plot_idea)

    def test_web_payload_rejects_unknown_theme(self) -> None:
        with self.assertRaisesRegex(ValueError, "主题"):
            story_request_from_payload(
                {
                    "name": "小雨",
                    "age": 7,
                    "interest": "恐龙",
                    "setting": "月光森林",
                    "theme": "scary",
                }
            )

    def test_integrated_page_has_api_and_picturebook_controls(self) -> None:
        html = (PROJECT_ROOT / "src" / "web" / "index.html").read_text(encoding="utf-8")
        for element_id in [
            "storySetting",
            "generationStatus",
            "generateButton",
            "polishButton",
            "storySourceNote",
            "plotIdea",
            "voiceButton",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
        self.assertIn('href="picturebook/"', html)
        self.assertIn('href="audiobook/"', html)
        self.assertIn('href="video/"', html)
        self.assertIn('href="library/"', html)
        self.assertIn('href="agent/"', html)
        self.assertIn('href="motion/"', html)

    def test_frontend_does_not_contain_api_key(self) -> None:
        script = (PROJECT_ROOT / "src" / "web" / "assets" / "app.js").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("LLM_API_KEY", script)
        self.assertIn('requestJson("api/story"', script)
        self.assertIn('requestJson("api/polish"', script)


if __name__ == "__main__":
    unittest.main()
