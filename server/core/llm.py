from __future__ import annotations

import json
from typing import Any, Protocol

import httpx

from server.config import Settings


class ChatClient(Protocol):
    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Return a JSON object from a chat completion."""


class LlmConfigurationError(ValueError):
    pass


class OpenAICompatibleChatClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"LLM provider request failed with status {exc.response.status_code}."
            ) from exc

        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "LLM provider response did not match chat completion schema."
            ) from exc

        try:
            decoded = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM provider response content was not valid JSON.") from exc

        if not isinstance(decoded, dict):
            raise RuntimeError("LLM provider JSON response must be an object.")
        return decoded


def build_chat_client(settings: Settings) -> ChatClient | None:
    provider = settings.llm_provider.strip().lower()
    if provider in {"", "deterministic", "none"}:
        return None
    if provider != "openai_compatible":
        raise LlmConfigurationError(f"Unsupported LLM provider: {settings.llm_provider}")
    if not settings.llm_base_url:
        raise LlmConfigurationError("AGL_LLM_BASE_URL is required for openai_compatible.")
    if not settings.llm_api_key:
        raise LlmConfigurationError("AGL_LLM_API_KEY is required for openai_compatible.")
    if not settings.llm_model:
        raise LlmConfigurationError("AGL_LLM_MODEL is required for openai_compatible.")
    return OpenAICompatibleChatClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
