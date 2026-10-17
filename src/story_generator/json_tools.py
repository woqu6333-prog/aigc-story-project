"""清理并提取模型回复中的JSON对象。"""

from __future__ import annotations

import json
import re
from typing import Any


class JSONExtractionError(ValueError):
    """回复中没有可解析的JSON对象。"""


FENCE_PATTERN = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def extract_first_json_object(text: str) -> dict[str, Any]:
    if not text or not text.strip():
        raise JSONExtractionError("模型返回了空内容")

    cleaned = text.lstrip("\ufeff").strip()
    cleaned = FENCE_PATTERN.sub("", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise JSONExtractionError("顶层JSON必须是对象")
        return parsed
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise JSONExtractionError("回复中没有找到JSON对象起始符号")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(cleaned)):
        character = cleaned[index]

        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue

        if character == '"':
            in_string = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start : index + 1]
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError as exc:
                    raise JSONExtractionError(f"找到JSON片段但解析失败：{exc}") from exc
                if not isinstance(parsed, dict):
                    raise JSONExtractionError("顶层JSON必须是对象")
                return parsed

    raise JSONExtractionError("JSON对象不完整，可能是输出被截断")
