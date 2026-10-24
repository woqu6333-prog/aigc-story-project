#!/usr/bin/env python
"""生成单个结构化儿童故事。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_generator.client import OpenAICompatibleClient  # noqa: E402
from story_generator.config import ConfigurationError, LLMConfig  # noqa: E402
from story_generator.models import StoryRequest  # noqa: E402
from story_generator.prompts import PromptStrategy, build_messages  # noqa: E402
from story_generator.service import StoryGenerationError, StoryGenerator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="作业1：结构化儿童故事生成器")
    parser.add_argument("--name", required=True, help="主角名字")
    parser.add_argument("--age", type=int, required=True, help="主角年龄，3至15岁")
    parser.add_argument("--interest", required=True, help="主角兴趣")
    parser.add_argument("--setting", required=True, help="故事发生场景")
    parser.add_argument("--theme", choices=["勇气", "友谊", "环保"], required=True)
    parser.add_argument("--length", choices=["短篇", "中篇", "长篇"], default="中篇")
    parser.add_argument("--target-age", type=int, required=True, help="目标读者年龄，3至12岁")
    parser.add_argument("--plot-idea", default="", help="用户自由剧情设想，最多500字")
    parser.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in PromptStrategy],
        default=PromptStrategy.ROLE_CONSTRAINTS.value,
    )
    parser.add_argument("--output", type=Path, help="自定义JSON输出路径")
    parser.add_argument(
        "--dry-run", action="store_true", help="只显示Prompt，不调用API"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        request = StoryRequest(
            hero_name=args.name,
            hero_age=args.age,
            interest=args.interest,
            setting=args.setting,
            theme=args.theme,
            story_length=args.length,
            target_age=args.target_age,
            plot_idea=args.plot_idea,
        )
        strategy = PromptStrategy(args.strategy)
    except ValueError as exc:
        print(f"输入参数错误：{exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(json.dumps(build_messages(strategy, request), ensure_ascii=False, indent=2))
        return 0

    try:
        config = LLMConfig.from_env()
        generator = StoryGenerator(
            OpenAICompatibleClient(config), max_retries=config.max_retries
        )
        result = generator.generate(request, strategy)
    except (ConfigurationError, RuntimeError, StoryGenerationError) as exc:
        print(f"生成失败：{exc}", file=sys.stderr)
        return 1

    output_path = args.output or _default_output_path(request.hero_name, strategy)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        result.story.model_dump_json(indent=2), encoding="utf-8"
    )

    print(f"生成成功：{output_path}")
    print(f"Prompt策略：{result.strategy.value}")
    print(f"API尝试次数：{result.attempts}")
    print(f"耗时：{result.elapsed_seconds:.2f}秒")
    return 0


def _default_output_path(hero_name: str, strategy: PromptStrategy) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = "".join(character for character in hero_name if character.isalnum()) or "story"
    return PROJECT_ROOT / "outputs" / "stories" / f"{timestamp}-{safe_name}-{strategy.value}.json"


if __name__ == "__main__":
    raise SystemExit(main())
