from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_agent import TOOL_NAMES, StoryCreationAgent


class Homework6AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agent = StoryCreationAgent(PROJECT_ROOT)
        cls.output = PROJECT_ROOT / "outputs" / "agent" / "homework6"

    def test_agent_registers_at_least_four_langchain_tools(self) -> None:
        self.assertGreaterEqual(len(TOOL_NAMES), 4)
        self.assertEqual(set(TOOL_NAMES), set(self.agent.tools))
        for tool in self.agent.tools.values():
            self.assertTrue(hasattr(tool, "invoke"))

    def test_plan_and_intervention_update_state(self) -> None:
        state = self.agent.create_state("unit-case", "男孩去森林寻找小鸟")
        plan = self.agent.plan(state)
        self.assertEqual(len(plan), 5)
        state.materials = {"old": True}
        state.story = {"old": True}
        state.artifacts = {"old": True}
        changed = self.agent.intervene(state, "主角改成女孩，场景换到海底")
        self.assertEqual(changed["protagonist"], "小星")
        self.assertIn("海底", changed["setting"])
        self.assertEqual(state.materials, {})
        self.assertEqual(state.story, {})
        self.assertEqual(state.artifacts, {})

    def test_two_complete_cases_have_all_artifacts(self) -> None:
        for case_id in ("case-01-space", "case-02-ocean"):
            case_dir = self.output / case_id
            with self.subTest(case_id=case_id):
                state = json.loads((case_dir / "agent-state.json").read_text(encoding="utf-8"))
                self.assertEqual(state["status"], "completed")
                self.assertEqual(len(state["artifacts"]["images"]), 3)
                self.assertGreater(state["artifacts"]["audio_duration_seconds"], 30)
                self.assertGreater(state["artifacts"]["video_duration_seconds"], 30)
                for filename in ("story.json", "narration.mp3", "story-video.mp4", "workflow-log.json"):
                    self.assertGreater((case_dir / filename).stat().st_size, 1_000)

    def test_workflow_logs_record_intervention_and_five_tools(self) -> None:
        expected = {"human_intervention", *TOOL_NAMES}
        for log_path in self.output.glob("case-*/workflow-log.json"):
            log = json.loads(log_path.read_text(encoding="utf-8"))
            actions = {entry["action"] for entry in log}
            self.assertTrue(expected.issubset(actions))
            self.assertTrue(all(entry["status"] == "completed" for entry in log))

    def test_agent_web_distribution(self) -> None:
        dist = PROJECT_ROOT / "dist" / "agent"
        for case_id in ("case-01-space", "case-02-ocean"):
            self.assertTrue((dist / "data" / f"{case_id}.json").is_file())
            self.assertGreater((dist / "media" / case_id / "story-video.mp4").stat().st_size, 500_000)


if __name__ == "__main__":
    unittest.main()
