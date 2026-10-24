#!/usr/bin/env python
"""用本地ComfyUI与MiniMax H3生成一个真实动态故事镜头。"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from h3_video import ComfyUIClient, build_h3_api_workflow, build_ref2va_prompt  # noqa: E402


DEFAULT_WORKFLOW = Path(r"D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI (1)\ComfyUI\user\default\workflows\video_minimax_h3_r2v.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成MiniMax H3儿童故事动态镜头")
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--character", type=Path, default=PROJECT_ROOT / "outputs" / "images" / "homework2" / "xiaoyu-character-sheet.png")
    parser.add_argument("--scene", type=Path, default=PROJECT_ROOT / "outputs" / "images" / "homework2" / "scene-01.png")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "outputs" / "video" / "h3" / "scene-01-h3.mp4")
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--megapixels", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=20261024)
    parser.add_argument("--quality", choices=("fast", "full"), default="fast", help="fast=4步Turbo，full=20步完整采样")
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt = build_ref2va_prompt(
        character_name="Xiaoyu",
        action="she traces the nearest footprint with one index finger, slowly raises her gaze along the trail, and shows a quiet spark of discovery",
        scene="a wet moonlit forest path after rain",
        mood="gentle curiosity turning into calm courage",
        duration=args.duration,
    )
    ui_workflow = json.loads(args.workflow.read_text(encoding="utf-8"))
    client = ComfyUIClient(args.server)
    stats = client.health()
    print(f"ComfyUI已连接：{stats['system']['os']}，设备数 {len(stats.get('devices', []))}", flush=True)
    character_name = client.upload_image(args.character)
    scene_name = client.upload_image(args.scene)
    workflow = build_h3_api_workflow(
        ui_workflow,
        prompt=prompt,
        character_image=character_name,
        scene_image=scene_name,
        duration=args.duration,
        megapixels=args.megapixels,
        seed=args.seed,
        filename_prefix="video/Story_H3_scene_01",
        quality=args.quality,
    )
    manifest = {
        "mode": "MiniMax H3 Ref2VA",
        "character_reference": str(args.character),
        "scene_reference": str(args.scene),
        "duration_seconds": args.duration,
        "megapixels": args.megapixels,
        "seed": args.seed,
        "quality": args.quality,
        "prompt": prompt,
        "api_workflow": workflow,
    }
    manifest_path = args.output.with_suffix(".json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.dry_run:
        print(f"H3工作流已构建但未排队：{manifest_path}")
        return
    started = time.perf_counter()
    prompt_id = client.queue(workflow)
    print(f"已进入H3队列：{prompt_id}", flush=True)
    history = client.wait(prompt_id)
    result = client.download_first_video(history, args.output)
    elapsed = round(time.perf_counter() - started, 2)
    manifest.update({"prompt_id": prompt_id, "elapsed_seconds": elapsed, "result": result})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"H3镜头生成完成：{args.output}，耗时{elapsed}秒", flush=True)


if __name__ == "__main__":
    main()
