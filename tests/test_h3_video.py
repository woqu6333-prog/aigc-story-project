from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from h3_video import build_h3_api_workflow, build_ref2va_prompt, convert_ui_workflow


class H3VideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_path = Path(r"D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI (1)\ComfyUI\user\default\workflows\video_minimax_h3_r2v.json")

    def test_prompt_uses_required_ref2va_sections(self) -> None:
        prompt = build_ref2va_prompt(character_name="Xiaoyu", action="she follows one footprint", scene="forest", mood="curious", duration=5)
        sections = ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"]
        positions = [prompt.index(section) for section in sections]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("<Picture 1>", prompt)
        self.assertIn("<Picture 2>", prompt)

    def test_prompt_rejects_invalid_duration(self) -> None:
        with self.assertRaises(ValueError):
            build_ref2va_prompt(character_name="X", action="walks", scene="forest", mood="calm", duration=3)

    def test_workflow_converts_and_enables_turbo_lora(self) -> None:
        if not self.workflow_path.exists():
            self.skipTest("本机没有H3工作流")
        ui = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        api = convert_ui_workflow(ui)
        self.assertEqual(api["136"]["class_type"], "MiniMaxH3ReferenceToVideo")
        generated = build_h3_api_workflow(ui, prompt="six-section prompt", character_image="character.png", scene_image="scene.png")
        self.assertTrue(generated["146"]["inputs"]["value"])
        self.assertEqual(generated["144"]["inputs"]["value"], 4)
        self.assertEqual(generated["157"]["inputs"]["image"], "character.png")
        self.assertEqual(generated["158"]["inputs"]["image"], "scene.png")
        self.assertNotIn("160", generated)
        self.assertNotIn("ref_images.ref_image_2", generated["136"]["inputs"])
        self.assertEqual(generated["124"]["inputs"]["scheduler"], "simple")

        full = build_h3_api_workflow(ui, prompt="six-section prompt", character_image="character.png", scene_image="scene.png", quality="full")
        self.assertFalse(full["146"]["inputs"]["value"])
        self.assertEqual(full["124"]["inputs"]["scheduler"], "normal")


if __name__ == "__main__":
    unittest.main()
