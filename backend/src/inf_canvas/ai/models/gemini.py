"""Gemini model client (google-genai SDK) — the default provider."""

from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from ...config import Role, Settings
from .base import Image, ModelError

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.google_api_key:
            raise ModelError(
                "GOOGLE_API_KEY is not set. Add it to the repo-root .env to use the Gemini agents."
            )
        self._client = genai.Client(api_key=settings.google_api_key)
        self.settings = settings

    def _contents(self, prompt: str, image: Image | None) -> list[Any]:
        if image:
            return [types.Part.from_bytes(data=image[0], mime_type=image[1]), prompt]
        return [prompt]

    def generate_structured(
        self,
        *,
        role: Role,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        image: Image | None = None,
        temperature: float = 0.2,
    ) -> T:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction=system,
            temperature=temperature,
        )
        resp = self._client.models.generate_content(
            model=self.settings.model_id(role),
            contents=self._contents(prompt, image),
            config=config,
        )
        parsed = resp.parsed
        if isinstance(parsed, schema):
            return parsed
        if resp.text:
            return schema.model_validate_json(resp.text)
        raise ModelError("Model returned no parseable structured output.")

    def generate_text(
        self,
        *,
        role: Role,
        prompt: str,
        system: str | None = None,
        image: Image | None = None,
        temperature: float = 0.4,
    ) -> str:
        config = types.GenerateContentConfig(system_instruction=system, temperature=temperature)
        resp = self._client.models.generate_content(
            model=self.settings.model_id(role),
            contents=self._contents(prompt, image),
            config=config,
        )
        return resp.text or ""
