"""从作业1故事JSON生成作业2配图提示词清单。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from illustration.prompt_builder import build_prompt_manifest
from story_generator.models import StoryOutput


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成角色一致的绘本配图提示词")
    parser.add_argument(
        "--story",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "stories" / "homework2-demo-story.json",
        help="作业1结构化故事JSON路径",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "prompts" / "homework2-illustration-prompts.json",
        help="提示词清单输出路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_story = json.loads(args.story.read_text(encoding="utf-8"))
    story = StoryOutput.model_validate(raw_story)
    manifest = build_prompt_manifest(story.model_dump())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"配图提示词已生成：{args.output}")


if __name__ == "__main__":
    main()
