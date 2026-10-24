"""ComfyUI HTTP客户端：上传参考图、排队、轮询和下载生成文件。"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx


class ComfyUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self.http = httpx.Client(base_url=self.base_url, timeout=timeout)

    def health(self) -> dict[str, Any]:
        response = self.http.get("/system_stats")
        response.raise_for_status()
        return response.json()

    def upload_image(self, path: Path, *, subfolder: str = "aigc_story_project") -> str:
        path = Path(path)
        with path.open("rb") as source:
            response = self.http.post(
                "/upload/image",
                data={"type": "input", "subfolder": subfolder, "overwrite": "true"},
                files={"image": (path.name, source, "image/png")},
            )
        response.raise_for_status()
        payload = response.json()
        folder = str(payload.get("subfolder", "")).strip("/\\")
        return f"{folder}/{payload['name']}" if folder else str(payload["name"])

    def queue(self, workflow: dict[str, Any]) -> str:
        response = self.http.post("/prompt", json={"prompt": workflow, "client_id": self.client_id})
        if response.status_code >= 400:
            raise RuntimeError(f"ComfyUI拒绝工作流：{response.text}")
        payload = response.json()
        if payload.get("node_errors"):
            raise RuntimeError(f"ComfyUI工作流校验失败：{payload['node_errors']}")
        return str(payload["prompt_id"])

    def wait(self, prompt_id: str, *, timeout_seconds: float = 7200, poll_seconds: float = 5) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self.http.get(f"/history/{prompt_id}")
            response.raise_for_status()
            history = response.json()
            if prompt_id in history:
                result = history[prompt_id]
                status = result.get("status", {})
                if status.get("status_str") == "error" or status.get("completed") is False:
                    messages = status.get("messages", [])
                    raise RuntimeError(f"ComfyUI生成失败：{messages}")
                return result
            time.sleep(poll_seconds)
        raise TimeoutError(f"等待H3生成超过{timeout_seconds:.0f}秒")

    def download_first_video(self, history: dict[str, Any], destination: Path) -> dict[str, Any]:
        candidates: list[dict[str, Any]] = []
        for output in history.get("outputs", {}).values():
            for key in ("videos", "gifs", "images"):
                candidates.extend(output.get(key, []))
        if not candidates:
            raise RuntimeError("ComfyUI历史记录中没有找到视频输出")
        file_info = candidates[0]
        query = urlencode({"filename": file_info["filename"], "subfolder": file_info.get("subfolder", ""), "type": file_info.get("type", "output")})
        response = self.http.get(f"/view?{query}", timeout=300)
        response.raise_for_status()
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
        return {**file_info, "downloaded_to": str(destination), "size_bytes": destination.stat().st_size}
