"""构建作业0主页与作业2网页绘本。仅使用 Python 标准库。"""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "src" / "web"
PICTUREBOOK_DIR = PROJECT_ROOT / "src" / "picturebook"
PICTUREBOOK_IMAGES = PROJECT_ROOT / "outputs" / "images" / "homework2"
PICTUREBOOK_STORY = PROJECT_ROOT / "outputs" / "stories" / "homework2-demo-story.json"
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
    print(f"静态网站已生成：{DIST_DIR}")


if __name__ == "__main__":
    build()
