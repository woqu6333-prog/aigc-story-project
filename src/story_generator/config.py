"""从环境变量读取兼容不同服务商的大模型配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigurationError(RuntimeError):
    """环境变量缺失或格式错误。"""


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class LLMConfig:
    api_key: str
    model: str
    base_url: str | None = None
    json_mode: bool = False
    timeout_seconds: float = 60.0
    max_retries: int = 2
    temperature: float = 0.7
    max_tokens: int = 3000

    @classmethod
    def from_env(cls) -> "LLMConfig":
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise ConfigurationError(
                "缺少python-dotenv，请先执行：python -m pip install -r requirements.txt"
            ) from exc

        load_dotenv()
        api_key = os.getenv("LLM_API_KEY", "").strip()
        model = os.getenv("LLM_MODEL", "").strip()
        base_url = os.getenv("LLM_BASE_URL", "").strip()

        # Gemini官方提供OpenAI兼容端点。允许只填写GEMINI_API_KEY，
        # 这样初学者不需要重复配置三个字段，且密钥仍只留在本机后端。
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if (not api_key or api_key == "your_api_key_here") and gemini_key:
            api_key = gemini_key
            if not model or model == "your_model_name_here":
                model = "gemini-3.8-flash"
            if not base_url or "provider.example.com" in base_url:
                base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        if not api_key or api_key == "your_api_key_here":
            raise ConfigurationError("请在.env中设置真实的LLM_API_KEY")
        if not model or model == "your_model_name_here":
            raise ConfigurationError("请在.env中设置LLM_MODEL")

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url or None,
            json_mode=_as_bool(os.getenv("LLM_JSON_MODE")),
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "3000")),
        )
