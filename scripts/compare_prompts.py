#!/usr/bin/env python
"""用相同输入依次运行三种Prompt策略，生成对比素材。"""

from __future__ import annotations

import argparse
import csv
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
from story_generator.prompts import PromptStrategy  # noqa: E402
from story_generator.service import StoryGenerationError, StoryGenerator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行三种Prompt策略对比实验")
    parser.add_argument("--name", required=True)
    parser.add_argument("--age", type=int, required=True)
    parser.add_argument("--interest", required=True)
    parser.add_argument("--setting", required=True)
    parser.add_argument("--theme", choices=["勇气", "友谊", "环保"], required=True)
    parser.add_argument("--length", choices=["短篇", "中篇", "长篇"], default="中篇")
    parser.add_argument("--target-age", type=int, required=True)
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
        )
        config = LLMConfig.from_env()
    except (ValueError, ConfigurationError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    run_dir = (
        PROJECT_ROOT
        / "outputs"
        / "stories"
        / f"prompt-comparison-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    generator = StoryGenerator(
        OpenAICompatibleClient(config), max_retries=config.max_retries
    )
    rows: list[dict[str, object]] = []

    for strategy in PromptStrategy:
        try:
            result = generator.generate(request, strategy)
            output_path = run_dir / f"{strategy.value}.json"
            output_path.write_text(
                result.story.model_dump_json(indent=2), encoding="utf-8"
            )
            rows.append(
                {
                    "strategy": strategy.value,
                    "success": True,
                    "attempts": result.attempts,
                    "elapsed_seconds": f"{result.elapsed_seconds:.2f}",
                    "scene_count": len(result.story.scenes),
                    "character_count": len(result.story.characters),
                    "output_file": output_path.name,
                    "error": "",
                }
            )
            print(f"[成功] {strategy.value}: {output_path.name}")
        except (RuntimeError, StoryGenerationError) as exc:
            rows.append(
                {
                    "strategy": strategy.value,
                    "success": False,
                    "attempts": "",
                    "elapsed_seconds": "",
                    "scene_count": "",
                    "character_count": "",
                    "output_file": "",
                    "error": str(exc),
                }
            )
            print(f"[失败] {strategy.value}: {exc}", file=sys.stderr)

    csv_path = run_dir / "automatic-metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"对比结果目录：{run_dir}")
    return 0 if all(row["success"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
