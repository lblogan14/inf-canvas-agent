"""Generic model client for non-Gemini providers via LangChain.

Uses `init_chat_model`, so any provider LangChain supports works (openai,
anthropic, google_genai, groq, mistral, ...). Requires the optional `providers`
extra: `uv sync --extra providers` (or `pip install 'inf-canvas[providers]'`).
"""

import base64
from typing import Any, TypeVar

from pydantic import BaseModel

from ...config import Role, Settings
from .base import Image, ModelError

T = TypeVar("T", bound=BaseModel)


class LangChainClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache: dict[Role, Any] = {}

    def _model(self, role: Role) -> Any:
        if role not in self._cache:
            try:
                from langchain.chat_models import init_chat_model
            except ImportError as err:  # pragma: no cover - optional dependency
                raise ModelError(
                    f"Provider '{self.settings.llm_provider}' needs the optional deps. "
                    "Install them with: uv sync --extra providers"
                ) from err
            self._cache[role] = init_chat_model(
                self.settings.model_id(role), model_provider=self.settings.llm_provider
            )
        return self._cache[role]

    def _messages(self, prompt: str, system: str | None, image: Image | None) -> list[Any]:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages: list[Any] = []
        if system:
            messages.append(SystemMessage(system))
        if image:
            b64 = base64.b64encode(image[0]).decode()
            messages.append(
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{image[1]};base64,{b64}"},
                        },
                    ]
                )
            )
        else:
            messages.append(HumanMessage(prompt))
        return messages

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
        model = self._model(role)
        result = model.with_structured_output(schema).invoke(self._messages(prompt, system, image))
        if not isinstance(result, schema):
            raise ModelError("Model returned no parseable structured output.")
        return result

    def generate_text(
        self,
        *,
        role: Role,
        prompt: str,
        system: str | None = None,
        image: Image | None = None,
        temperature: float = 0.4,
    ) -> str:
        model = self._model(role)
        resp = model.invoke(self._messages(prompt, system, image))
        return str(resp.content)
