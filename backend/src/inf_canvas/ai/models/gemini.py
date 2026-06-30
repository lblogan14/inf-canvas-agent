"""Thin wrapper around the `google-genai` SDK.

Centralizes client creation, model selection (Pro vs Flash), and structured
JSON output. No agent logic lives here.
"""

from functools import lru_cache
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from ...config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


class GeminiError(RuntimeError):
    """Raised when Gemini is unavailable or returns unusable output."""


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.has_api_key:
            raise GeminiError(
                "GOOGLE_API_KEY is not set. Add it to the repo-root .env to use the AI agents."
            )
        self._client = genai.Client(api_key=settings.google_api_key)
        self.settings = settings

    def generate_structured(
        self,
        *,
        model: str,
        contents: Any,
        schema: type[T],
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> T:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction=system_instruction,
            temperature=temperature,
        )
        resp = self._client.models.generate_content(model=model, contents=contents, config=config)
        parsed = resp.parsed
        if isinstance(parsed, schema):
            return parsed
        if resp.text:
            return schema.model_validate_json(resp.text)
        raise GeminiError("Gemini returned no parseable structured output.")

    def generate_text(
        self,
        *,
        model: str,
        contents: Any,
        system_instruction: str | None = None,
        temperature: float = 0.4,
    ) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        )
        resp = self._client.models.generate_content(model=model, contents=contents, config=config)
        return resp.text or ""

    @staticmethod
    def image_part(data: bytes, mime_type: str) -> types.Part:
        return types.Part.from_bytes(data=data, mime_type=mime_type)


@lru_cache
def get_gemini_client() -> GeminiClient:
    """Cached client. Raises GeminiError if no API key is configured."""
    return GeminiClient(get_settings())
