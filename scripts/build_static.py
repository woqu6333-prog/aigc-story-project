"""构建作业0–6统一静态演示网站。"""

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
VIDEO_DIR = PROJECT_ROOT / "src" / "video_web"
VIDEO_OUTPUT = PROJECT_ROOT / "outputs" / "video" / "homework4"
LIBRARY_DIR = PROJECT_ROOT / "src" / "library_web"
LIBRARY_OUTPUT = PROJECT_ROOT / "outputs" / "library" / "homework5"
AGENT_DIR = PROJECT_ROOT / "src" / "agent_web"
AGENT_OUTPUT = PROJECT_ROOT / "outputs" / "agent" / "homework6"
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
    if not VIDEO_DIR.exists():
        raise FileNotFoundError(f"找不到短视频网页源码：{VIDEO_DIR}")
    for required_video_file in ("xiaoyu-story-video.mp4", "thumbnail.jpg", "video-plan.json"):
        path = VIDEO_OUTPUT / required_video_file
        if not path.exists():
            raise FileNotFoundError(f"找不到作业4视频成果：{path}")
    if not LIBRARY_DIR.exists() or not (LIBRARY_OUTPUT / "index.json").exists():
        raise FileNotFoundError("找不到作业5素材库，请先运行scripts/build_material_library.py")
    if not AGENT_DIR.exists():
        raise FileNotFoundError(f"找不到作业6网页源码：{AGENT_DIR}")
    for case_id in ("case-01-space", "case-02-ocean"):
        for filename in ("agent-state.json", "story-video.mp4"):
            path = AGENT_OUTPUT / case_id / filename
            if not path.exists():
                raise FileNotFoundError(f"找不到作业6案例成果：{path}")

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

    video_dist = DIST_DIR / "video"
    shutil.copytree(VIDEO_DIR, video_dist, dirs_exist_ok=True)
    video_assets = video_dist / "assets"
    video_media = video_assets / "video"
    video_media.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VIDEO_OUTPUT / "xiaoyu-story-video.mp4", video_media / "xiaoyu-story-video.mp4")
    shutil.copy2(VIDEO_OUTPUT / "thumbnail.jpg", video_assets / "thumbnail.jpg")
    video_data = video_dist / "data"
    video_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VIDEO_OUTPUT / "video-plan.json", video_data / "video-plan.json")

    library_dist = DIST_DIR / "library"
    shutil.copytree(LIBRARY_DIR, library_dist, dirs_exist_ok=True)
    shutil.copytree(LIBRARY_OUTPUT / "assets", library_dist / "assets", dirs_exist_ok=True)
    library_data = library_dist / "data"
    library_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LIBRARY_OUTPUT / "index.json", library_data / "index.json")
    shutil.copy2(LIBRARY_OUTPUT / "evaluation.json", library_data / "evaluation.json")

    agent_dist = DIST_DIR / "agent"
    shutil.copytree(AGENT_DIR, agent_dist, dirs_exist_ok=True)
    agent_data = agent_dist / "data"
    agent_media = agent_dist / "media"
    agent_data.mkdir(parents=True, exist_ok=True)
    for case_id in ("case-01-space", "case-02-ocean"):
        shutil.copy2(AGENT_OUTPUT / case_id / "agent-state.json", agent_data / f"{case_id}.json")
        case_media = agent_media / case_id
        case_media.mkdir(parents=True, exist_ok=True)
        shutil.copy2(AGENT_OUTPUT / case_id / "story-video.mp4", case_media / "story-video.mp4")
    print(f"静态网站已生成：{DIST_DIR}")


if __name__ == "__main__":
    build()
