"""将作业0静态网站从 src/web 同步到 dist。仅使用 Python 标准库。"""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "src" / "web"
DIST_DIR = PROJECT_ROOT / "dist"


def build() -> None:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"找不到网站源码目录：{SOURCE_DIR}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE_DIR, DIST_DIR, dirs_exist_ok=True)
    print(f"静态网站已生成：{DIST_DIR}")


if __name__ == "__main__":
    build()
