#!/usr/bin/env python
"""生成作业4故事短视频。"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_video import build_story_video


def main() -> None:
    report = build_story_video(
        timeline_path=PROJECT_ROOT / "outputs" / "audio" / "homework3" / "timeline.json",
        audiobook_path=PROJECT_ROOT / "outputs" / "audio" / "homework3" / "audiobook.mp3",
        images_dir=PROJECT_ROOT / "outputs" / "images" / "homework2",
        output_dir=PROJECT_ROOT / "outputs" / "video" / "homework4",
    )
    duration = float(report["actual_duration_seconds"])
    print(f"作业4视频已生成：outputs/video/homework4/{report['output_file']}")
    print(f"实际时长：{int(duration // 60)}分{int(duration % 60):02d}秒")
    print(f"分辨率：{report['resolution']}，帧率：{report['fps']}fps")
    print(f"视频编码器：{report['video_encoder']}")


if __name__ == "__main__":
    main()
