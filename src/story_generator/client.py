"""OpenAI兼容Chat Completions客户端封装。"""

from __future__ import annotations

import time
from typing import Protocol

from .config import LLMConfig


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class OpenAICompatibleClient:
    def __init__(self, config: LLMConfig) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "缺少openai包，请先执行：python -m pip install -r requirements.txt"
            ) from exc

        client_kwargs: dict[str, object] = {
            "api_key": config.api_key,
            "timeout": config.timeout_seconds,
            "max_retries": 0,
        }
        if config.base_url:
            client_kwargs["base_url"] = config.base_url

        self._client = OpenAI(**client_kwargs)
        self._config = config

    def complete(self, messages: list[dict[str, str]]) -> str:
        request_kwargs: dict[str, object] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
        }
        if self._config.json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}

        response = None
        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.chat.completions.create(**request_kwargs)
                break
            except Exception as exc:
                status_code = getattr(exc, "status_code", None)
                is_temporary = status_code in {408, 429, 500, 502, 503, 504}
                if is_temporary and attempt < self._config.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if status_code == 503:
                    raise RuntimeError("模型当前请求量过高，请稍后重试或换用Flash-Lite模型") from exc
                if status_code == 429:
                    raise RuntimeError("API免费额度或请求频率已达到限制，请稍后重试") from exc
                raise RuntimeError(f"大模型API调用失败：{exc}") from exc

        if response is None:  # pragma: no cover - 防御性分支
            raise RuntimeError("大模型API没有返回结果")
        choice = response.choices[0]

        if choice.finish_reason == "length":
            raise RuntimeError("模型输出达到长度限制，JSON可能不完整；请提高LLM_MAX_TOKENS")
        if choice.finish_reason == "content_filter":
            raise RuntimeError("模型输出被内容安全策略中断")

        content = choice.message.content
        if not content:
            refusal = getattr(choice.message, "refusal", None)
            if refusal:
                raise RuntimeError(f"模型拒绝生成：{refusal}")
            raise RuntimeError("模型返回了空内容")
        return content
