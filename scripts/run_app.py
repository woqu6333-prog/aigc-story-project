#!/usr/bin/env python
"""启动星光故事屋本地服务，并把作业1生成器安全接入网页。"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import uuid
from datetime import datetime
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_static import build  # noqa: E402
from story_generator.client import OpenAICompatibleClient  # noqa: E402
from story_generator.config import ConfigurationError, LLMConfig  # noqa: E402
from story_generator.models import StoryOutput, StoryRequest  # noqa: E402
from story_generator.prompts import PromptStrategy  # noqa: E402
from story_generator.service import StoryGenerationError, StoryGenerator  # noqa: E402
from h3_video import ComfyUIClient, build_h3_api_workflow, build_ref2va_prompt  # noqa: E402


MAX_REQUEST_BYTES = 100_000
H3_WORKFLOW = Path(
    os.getenv(
        "H3_WORKFLOW_PATH",
        r"D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI (1)\ComfyUI\user\default\workflows\video_minimax_h3_r2v.json",
    )
)
H3_SERVER_URL = os.getenv("H3_COMFYUI_URL", "http://127.0.0.1:8188").strip()
H3_REFERENCE_DIR = PROJECT_ROOT / "outputs" / "images" / "homework2"
H3_JOBS: dict[str, dict[str, Any]] = {}
H3_LOCK = threading.Lock()
THEME_MAP = {
    "courage": "勇气",
    "friendship": "友谊",
    "nature": "环保",
    "勇气": "勇气",
    "友谊": "友谊",
    "环保": "环保",
}


def story_request_from_payload(payload: dict[str, Any]) -> StoryRequest:
    """把网页字段转换为作业1的严格输入模型。"""

    theme_value = str(payload.get("theme", "")).strip()
    if theme_value not in THEME_MAP:
        raise ValueError("主题必须是勇气、友谊或环保")
    age = int(payload.get("age", 0))
    return StoryRequest(
        hero_name=str(payload.get("name", "")).strip(),
        hero_age=age,
        interest=str(payload.get("interest", "")).strip(),
        setting=str(payload.get("setting", "月光森林")).strip(),
        theme=THEME_MAP[theme_value],  # type: ignore[arg-type]
        story_length=str(payload.get("story_length", "短篇")).strip(),  # type: ignore[arg-type]
        target_age=int(payload.get("target_age", age)),
        plot_idea=str(payload.get("plot_idea", "")).strip(),
    )


def h3_health() -> dict[str, Any]:
    try:
        stats = ComfyUIClient(H3_SERVER_URL, timeout=3).health()
    except Exception as exc:
        return {"available": False, "message": f"ComfyUI未启动：{exc}"}
    devices = stats.get("devices", [])
    device_name = devices[0].get("name", "GPU") if devices else "GPU"
    return {
        "available": H3_WORKFLOW.exists(),
        "message": "H3已就绪" if H3_WORKFLOW.exists() else "未找到H3工作流",
        "device": device_name,
        "estimated_seconds": 110,
    }


def run_h3_job(job_id: str, payload: dict[str, Any]) -> None:
    output_dir = PROJECT_ROOT / "outputs" / "video" / "h3" / "live"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{job_id}.mp4"
    manifest_path = output.with_suffix(".json")
    try:
        duration = max(4, min(8, int(payload.get("duration", 5))))
        action = str(payload.get("action", "")).strip() or (
            "she kneels beside the footprints, points to the nearest print, "
            "then looks ahead with a quiet spark of discovery"
        )
        mood = str(payload.get("mood", "gentle curiosity and calm courage")).strip()
        prompt = build_ref2va_prompt(
            character_name="Xiaoyu",
            action=action,
            scene="a wet moonlit forest path after rain",
            mood=mood,
            duration=duration,
        )
        client = ComfyUIClient(H3_SERVER_URL, timeout=60)
        character = client.upload_image(H3_REFERENCE_DIR / "xiaoyu-character-sheet.png")
        scene = client.upload_image(H3_REFERENCE_DIR / "scene-01.png")
        workflow = build_h3_api_workflow(
            json.loads(H3_WORKFLOW.read_text(encoding="utf-8")),
            prompt=prompt,
            character_image=character,
            scene_image=scene,
            duration=duration,
            megapixels=0.2,
            seed=int(payload.get("seed", 20261024)),
            filename_prefix=f"video/Story_H3_live_{job_id}",
            quality="fast",
        )
        prompt_id = client.queue(workflow)
        with H3_LOCK:
            H3_JOBS[job_id].update({"status": "running", "prompt_id": prompt_id})
        history = client.wait(prompt_id, timeout_seconds=900, poll_seconds=3)
        result = client.download_first_video(history, output)

        public_dir = DIST_DIR / "motion" / "media"
        public_dir.mkdir(parents=True, exist_ok=True)
        public_output = public_dir / f"{job_id}.mp4"
        public_output.write_bytes(output.read_bytes())
        manifest_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "mode": "MiniMax H3 Ref2VA",
                    "quality": "fast",
                    "duration_seconds": duration,
                    "prompt": prompt,
                    "result": result,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        with H3_LOCK:
            H3_JOBS[job_id].update(
                {
                    "status": "completed",
                    "video_url": f"/motion/media/{job_id}.mp4",
                    "message": "H3真实动态镜头生成完成",
                }
            )
    except Exception as exc:
        with H3_LOCK:
            H3_JOBS[job_id].update({"status": "failed", "message": str(exc)})


def save_story(story: StoryOutput, suffix: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = PROJECT_ROOT / "outputs" / "stories" / f"{timestamp}-{suffix}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(story.model_dump_json(indent=2), encoding="utf-8")
    return output


class StoryAppHandler(SimpleHTTPRequestHandler):
    server_version = "StarlightStoryHouse/1.0"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            self._handle_health()
            return
        if path == "/api/h3/health":
            self._send_json(HTTPStatus.OK, {"ok": True, **h3_health()})
            return
        if path.startswith("/api/h3/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            with H3_LOCK:
                job = H3_JOBS.get(job_id)
            if job is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "message": "任务不存在"})
            else:
                self._send_json(HTTPStatus.OK, {"ok": True, "job": job})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/story":
            self._handle_generate(polish=False)
            return
        if path == "/api/polish":
            self._handle_generate(polish=True)
            return
        if path == "/api/h3/generate":
            self._handle_h3_generate()
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "message": "接口不存在"})

    def _handle_health(self) -> None:
        try:
            config = LLMConfig.from_env()
        except (ConfigurationError, ValueError) as exc:
            self._send_json(
                HTTPStatus.OK,
                {"ok": True, "api_configured": False, "message": str(exc)},
            )
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "api_configured": True,
                "model": config.model,
                "message": "API已配置，可生成并润色故事",
            },
        )

    def _handle_h3_generate(self) -> None:
        health = h3_health()
        if not health["available"]:
            self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"ok": False, "message": health["message"]})
            return
        try:
            payload = self._read_json_body()
            if len(str(payload.get("action", ""))) > 400:
                raise ValueError("动作描述不能超过400个字符")
        except (ValueError, TypeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "message": str(exc)})
            return
        job_id = uuid.uuid4().hex[:12]
        with H3_LOCK:
            H3_JOBS[job_id] = {"id": job_id, "status": "queued", "message": "等待H3生成"}
        threading.Thread(target=run_h3_job, args=(job_id, payload), daemon=True).start()
        self._send_json(HTTPStatus.ACCEPTED, {"ok": True, "job_id": job_id, "estimated_seconds": 110})

    def _handle_generate(self, *, polish: bool) -> None:
        try:
            payload = self._read_json_body()
            request = story_request_from_payload(payload)
            config = LLMConfig.from_env()
            generator = StoryGenerator(
                OpenAICompatibleClient(config), max_retries=config.max_retries
            )
            if polish:
                story = StoryOutput.model_validate(payload.get("story"))
                result = generator.polish(request, story)
                suffix = "polished"
            else:
                strategy = PromptStrategy(
                    str(payload.get("strategy", PromptStrategy.ROLE_CONSTRAINTS.value))
                )
                result = generator.generate(request, strategy)
                suffix = result.strategy.value
            output = save_story(result.story, suffix)
        except (ValueError, TypeError) as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "code": "invalid_input", "message": str(exc)},
            )
            return
        except ConfigurationError as exc:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"ok": False, "code": "api_not_configured", "message": str(exc)},
            )
            return
        except (RuntimeError, StoryGenerationError) as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "code": "generation_failed", "message": str(exc)},
            )
            return
        except Exception as exc:  # 防止第三方SDK异常导致HTTP连接被直接中断
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "code": "provider_error", "message": f"云端服务暂时不可用：{exc}"},
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "story": result.story.model_dump(),
                "meta": {
                    "strategy": result.strategy.value,
                    "attempts": result.attempts,
                    "elapsed_seconds": round(result.elapsed_seconds, 2),
                    "polished": polish,
                    "saved_file": output.name,
                },
            },
        )

    def _read_json_body(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length无效") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("请求内容为空或过大")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("请求不是有效的UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("请求JSON必须是对象")
        return payload

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动星光故事屋本地API网站")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-build", action="store_true", help="启动前不重新构建dist")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.no_build:
        build()
    handler = partial(StoryAppHandler, directory=str(DIST_DIR))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"星光故事屋已启动：http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务。API密钥只从本地.env读取，不会发送给网页。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
