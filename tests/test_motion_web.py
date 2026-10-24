from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class MotionWebTests(unittest.TestCase):
    def test_motion_page_has_cached_and_live_paths(self) -> None:
        html = (PROJECT_ROOT / "src" / "motion_web" / "index.html").read_text(encoding="utf-8")
        script = (PROJECT_ROOT / "src" / "motion_web" / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("media/h3-reference.mp4", html)
        self.assertIn('id="generateButton"', html)
        self.assertIn("/api/h3/generate", script)
        self.assertIn("/api/h3/jobs/", script)

    def test_validated_h3_sample_exists(self) -> None:
        path = PROJECT_ROOT / "outputs" / "video" / "h3" / "scene-01-h3-fast-simple.mp4"
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 100_000)


if __name__ == "__main__":
    unittest.main()
