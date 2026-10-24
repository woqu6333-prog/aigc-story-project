#!/usr/bin/env python
"""运行作业6多模态故事Agent。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_agent import StoryCreationAgent  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成一个完整多模态故事案例")
    parser.add_argument("--case-id", required=True, help="例如 case-01")
    parser.add_argument("--idea", required=True, help="一句话故事创意")
    parser.add_argument("--intervene", default="", help="可选中途干预，例如：主角改成女孩，场景换到海底")
    parser.add_argument("--plan-only", action="store_true", help="只展示计划与干预结果，不生成媒体")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = StoryCreationAgent(PROJECT_ROOT)
    state = agent.create_state(args.case_id, args.idea)
    plan = agent.plan(state)
    print("Agent计划：")
    for step in plan:
        print(f"  {step['step']}. {step['tool']}：{step['purpose']}")
    if args.intervene:
        print("应用中途干预：", args.intervene)
        print(json.dumps(agent.intervene(state, args.intervene), ensure_ascii=False, indent=2))
    if args.plan_only:
        return
    result = agent.run(state)
    print("生成完成：")
    print(json.dumps(result.artifacts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
