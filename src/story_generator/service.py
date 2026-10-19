"""故事生成、校验和自动修复流程。"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from pydantic import ValidationError

from .client import ChatClient
from .json_tools import JSONExtractionError, extract_first_json_object
from .models import StoryOutput, StoryRequest
from .prompts import (
    PromptStrategy,
    build_messages,
    build_polish_messages,
    build_repair_messages,
)


class StoryGenerationError(RuntimeError):
    def __init__(self, message: str, raw_response: str = "") -> None:
        super().__init__(message)
        self.raw_response = raw_response


@dataclass(frozen=True, slots=True)
class GenerationResult:
    story: StoryOutput
    strategy: PromptStrategy
    attempts: int
    elapsed_seconds: float
    raw_response: str


class StoryGenerator:
    def __init__(self, client: ChatClient, max_retries: int = 2) -> None:
        self.client = client
        self.max_retries = max(0, max_retries)

    def generate(
        self, request: StoryRequest, strategy: PromptStrategy
    ) -> GenerationResult:
        return self._generate_from_messages(
            request=request,
            strategy=strategy,
            base_messages=build_messages(strategy, request),
        )

    def polish(self, request: StoryRequest, story: StoryOutput) -> GenerationResult:
        """对已校验故事进行第二遍文学润色，并再次执行全部结构校验。"""

        return self._generate_from_messages(
            request=request,
            strategy=PromptStrategy.ROLE_CONSTRAINTS,
            base_messages=build_polish_messages(request, story.model_dump()),
        )

    def _generate_from_messages(
        self,
        request: StoryRequest,
        strategy: PromptStrategy,
        base_messages: list[dict[str, str]],
    ) -> GenerationResult:
        started_at = perf_counter()
        active_messages = base_messages
        raw_response = ""
        last_error = ""

        for attempt in range(1, self.max_retries + 2):
            raw_response = self.client.complete(active_messages)
            try:
                payload = extract_first_json_object(raw_response)
                story = StoryOutput.model_validate(payload)
                story.ensure_request_alignment(request)
            except (JSONExtractionError, ValidationError, ValueError) as exc:
                last_error = _short_error(exc)
                if attempt > self.max_retries:
                    raise StoryGenerationError(
                        f"模型输出经过{attempt}次尝试仍未通过校验：{last_error}",
                        raw_response=raw_response,
                    ) from exc
                active_messages = build_repair_messages(
                    base_messages, raw_response, last_error
                )
                continue

            return GenerationResult(
                story=story,
                strategy=strategy,
                attempts=attempt,
                elapsed_seconds=perf_counter() - started_at,
                raw_response=raw_response,
            )

        raise StoryGenerationError(f"生成失败：{last_error}", raw_response=raw_response)


def _short_error(error: Exception, limit: int = 900) -> str:
    message = str(error).replace("https://errors.pydantic.dev", "Pydantic文档")
    return message if len(message) <= limit else f"{message[:limit]}..."
