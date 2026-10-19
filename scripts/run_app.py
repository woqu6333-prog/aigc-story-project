#!/usr/bin/env python
"""启动星光故事屋本地服务，并把作业1生成器安全接入网页。"""

from __future__ import annotations

import argparse
import json
import sys
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


MAX_REQUEST_BYTES = 100_000
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
    )


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
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/story":
            self._handle_generate(polish=False)
            return
        if path == "/api/polish":
            self._handle_generate(polish=True)
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
