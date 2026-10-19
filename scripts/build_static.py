"""构建作业0主页、作业2网页绘本与作业3同步有声书。"""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "src" / "web"
PICTUREBOOK_DIR = PROJECT_ROOT / "src" / "picturebook"
PICTUREBOOK_IMAGES = PROJECT_ROOT / "outputs" / "images" / "homework2"
PICTUREBOOK_STORY = PROJECT_ROOT / "outputs" / "stories" / "homework2-demo-story.json"
AUDIOBOOK_DIR = PROJECT_ROOT / "src" / "audiobook_web"
AUDIOBOOK_OUTPUT = PROJECT_ROOT / "outputs" / "audio" / "homework3"
AUDIOBOOK_SCRIPT = PROJECT_ROOT / "outputs" / "stories" / "homework3-audiobook-script.json"
DIST_DIR = PROJECT_ROOT / "dist"


def build() -> None:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"找不到网站源码目录：{SOURCE_DIR}")
    if not PICTUREBOOK_DIR.exists():
        raise FileNotFoundError(f"找不到绘本源码目录：{PICTUREBOOK_DIR}")
    if not PICTUREBOOK_IMAGES.exists():
        raise FileNotFoundError(f"找不到绘本图片目录：{PICTUREBOOK_IMAGES}")
    if not PICTUREBOOK_STORY.exists():
        raise FileNotFoundError(f"找不到绘本故事：{PICTUREBOOK_STORY}")
    if not AUDIOBOOK_DIR.exists():
        raise FileNotFoundError(f"找不到有声书网页源码：{AUDIOBOOK_DIR}")
    for required_audio_file in ("audiobook.mp3", "timeline.json"):
        path = AUDIOBOOK_OUTPUT / required_audio_file
        if not path.exists():
            raise FileNotFoundError(f"找不到有声书成果：{path}")
    if not AUDIOBOOK_SCRIPT.exists():
        raise FileNotFoundError(f"找不到有声书脚本：{AUDIOBOOK_SCRIPT}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE_DIR, DIST_DIR, dirs_exist_ok=True)
    picturebook_dist = DIST_DIR / "picturebook"
    shutil.copytree(PICTUREBOOK_DIR, picturebook_dist, dirs_exist_ok=True)
    shutil.copytree(
        PICTUREBOOK_IMAGES,
        picturebook_dist / "assets" / "images",
        dirs_exist_ok=True,
    )
    story_dist = picturebook_dist / "data" / "story.json"
    story_dist.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PICTUREBOOK_STORY, story_dist)

    audiobook_dist = DIST_DIR / "audiobook"
    shutil.copytree(AUDIOBOOK_DIR, audiobook_dist, dirs_exist_ok=True)
    audio_dist = audiobook_dist / "assets" / "audio"
    audio_dist.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AUDIOBOOK_OUTPUT / "audiobook.mp3", audio_dist / "audiobook.mp3")
    shutil.copy2(AUDIOBOOK_OUTPUT / "timeline.json", audio_dist / "timeline.json")
    audiobook_data = audiobook_dist / "data"
    audiobook_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AUDIOBOOK_SCRIPT, audiobook_data / "script.json")
    print(f"静态网站已生成：{DIST_DIR}")


if __name__ == "__main__":
    build()
