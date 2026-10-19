#!/usr/bin/env python
"""生成作业3多角色有声书与同步时间轴。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from audiobook.builder import build_audiobook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成多角色有声书")
    parser.add_argument(
        "--script",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "stories" / "homework3-audiobook-script.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "audio" / "homework3" / "audiobook.mp3",
    )
    parser.add_argument(
        "--timeline",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "audio" / "homework3" / "timeline.json",
    )
    parser.add_argument(
        "--force", action="store_true", help="忽略已生成分段并重新请求TTS"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parts_dir = args.output.parent / "parts"
    report = build_audiobook(
        args.script,
        args.output,
        args.timeline,
        parts_dir,
        force=args.force,
    )
    print(f"有声书已生成：{args.output}")
    print(f"总时长：{report['duration_display']}")
    print(f"角色：{'、'.join(report['roles'])}")
    print(f"不同音色：{report['voice_count']}种")


if __name__ == "__main__":
    main()
