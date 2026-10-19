from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_generator.json_tools import JSONExtractionError, extract_first_json_object
from story_generator.models import StoryOutput, StoryRequest
from story_generator.prompts import PromptStrategy, build_messages, build_polish_messages
from story_generator.service import StoryGenerationError, StoryGenerator


def valid_request() -> StoryRequest:
    return StoryRequest(
        hero_name="小雨",
        hero_age=7,
        interest="恐龙",
        setting="月光森林",
        theme="勇气",
        story_length="短篇",
        target_age=7,
    )


def valid_story_payload() -> dict[str, object]:
    return {
        "title": "小雨和月光脚印",
        "characters": [
            {
                "name": "小雨",
                "traits": "细心而勇敢",
                "appearance": "7岁女孩，黑色短发，黄色外套，背着恐龙图案小包",
            }
        ],
        "scenes": [
            {
                "scene_id": 1,
                "description": "小雨在森林入口发现奇怪脚印",
                "text": "小雨走进月光森林，在泥地上发现三趾脚印。喜欢恐龙的她认真观察，没有急着把脚印当成怪兽留下的。",
                "mood": "好奇",
                "visual_prompt": "儿童绘本，黑色短发女孩穿黄色外套，在月光森林观察三趾脚印",
            },
            {
                "scene_id": 2,
                "description": "小雨根据恐龙知识判断脚印来源",
                "text": "小雨想起恐龙图鉴中的比例知识，发现这些脚印很小，而且旁边还有羽毛，于是判断它们来自迷路的小鸟。",
                "mood": "专注",
                "visual_prompt": "儿童绘本，女孩对照恐龙图鉴观察小脚印，旁边有一片蓝色羽毛",
            },
            {
                "scene_id": 3,
                "description": "小雨帮助小鸟回家",
                "text": "小雨沿着脚印找到三只小鸟，并把它们送回树上的家。她明白，知识和勇气一起使用，才能真正帮助别人。",
                "mood": "温暖",
                "visual_prompt": "儿童绘本，黑色短发女孩把三只小鸟送回树巢，月光温暖柔和",
            },
        ],
        "moral": "勇气不是贸然向前，而是在认真观察后愿意采取行动。",
    }


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return self.responses[len(self.calls) - 1]


class JSONToolsTests(unittest.TestCase):
    def test_parses_plain_json(self) -> None:
        self.assertEqual(extract_first_json_object('{"title":"测试"}')["title"], "测试")

    def test_parses_fenced_json(self) -> None:
        parsed = extract_first_json_object('```json\n{"title":"测试"}\n```')
        self.assertEqual(parsed["title"], "测试")

    def test_extracts_json_from_extra_text(self) -> None:
        parsed = extract_first_json_object('结果如下：\n{"text":"包含 } 字符"}\n完成')
        self.assertEqual(parsed["text"], "包含 } 字符")

    def test_rejects_incomplete_json(self) -> None:
        with self.assertRaises(JSONExtractionError):
            extract_first_json_object('{"title":"没有结束"')


class ModelTests(unittest.TestCase):
    def test_valid_story_passes(self) -> None:
        story = StoryOutput.model_validate(valid_story_payload())
        story.ensure_request_alignment(valid_request())
        self.assertEqual(len(story.scenes), 3)

    def test_scene_ids_must_be_continuous(self) -> None:
        payload = valid_story_payload()
        payload["scenes"][1]["scene_id"] = 3  # type: ignore[index]
        with self.assertRaises(ValidationError):
            StoryOutput.model_validate(payload)

    def test_interest_must_enter_story(self) -> None:
        story = StoryOutput.model_validate(valid_story_payload())
        request = valid_request().model_copy(update={"interest": "足球"})
        with self.assertRaisesRegex(ValueError, "兴趣"):
            story.ensure_request_alignment(request)


class PromptTests(unittest.TestCase):
    def test_all_three_strategies_request_json(self) -> None:
        for strategy in PromptStrategy:
            with self.subTest(strategy=strategy):
                messages = build_messages(strategy, valid_request())
                combined = "\n".join(message["content"] for message in messages)
                self.assertIn("JSON", combined)
                self.assertIn("小雨", combined)
                self.assertIn("恐龙", combined)

    def test_role_strategy_contains_coherence_constraint(self) -> None:
        messages = build_messages(PromptStrategy.ROLE_CONSTRAINTS, valid_request())
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("因果关系", combined)
        self.assertIn("不能只机械重复兴趣名称", combined)
        self.assertIn("长短句交替", combined)
        self.assertIn("通过选择、行动和结果表现成长", combined)

    def test_polish_prompt_preserves_structure_and_improves_style(self) -> None:
        messages = build_polish_messages(valid_request(), valid_story_payload())
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("不改变故事核心事件", combined)
        self.assertIn("动作、感官细节或简短自然的对话", combined)
        self.assertIn("小雨和月光脚印", combined)


class ServiceTests(unittest.TestCase):
    def test_success_on_first_attempt(self) -> None:
        client = FakeClient([json.dumps(valid_story_payload(), ensure_ascii=False)])
        result = StoryGenerator(client, max_retries=2).generate(
            valid_request(), PromptStrategy.ZERO_SHOT
        )
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.story.title, "小雨和月光脚印")

    def test_invalid_output_is_repaired(self) -> None:
        client = FakeClient(
            ["这不是JSON", json.dumps(valid_story_payload(), ensure_ascii=False)]
        )
        result = StoryGenerator(client, max_retries=1).generate(
            valid_request(), PromptStrategy.ROLE_CONSTRAINTS
        )
        self.assertEqual(result.attempts, 2)
        self.assertIn("校验错误", client.calls[1][-1]["content"])

    def test_raises_after_retry_limit(self) -> None:
        client = FakeClient(["错误一", "错误二"])
        with self.assertRaises(StoryGenerationError):
            StoryGenerator(client, max_retries=1).generate(
                valid_request(), PromptStrategy.FEW_SHOT
            )

    def test_polish_reuses_validation_pipeline(self) -> None:
        polished_payload = valid_story_payload()
        polished_payload["scenes"][0]["text"] += "月光在水洼里轻轻晃动。"  # type: ignore[index]
        client = FakeClient([json.dumps(polished_payload, ensure_ascii=False)])
        original = StoryOutput.model_validate(valid_story_payload())
        result = StoryGenerator(client, max_retries=1).polish(valid_request(), original)
        self.assertEqual(result.attempts, 1)
        self.assertIn("月光", result.story.scenes[0].text)


if __name__ == "__main__":
    unittest.main()
