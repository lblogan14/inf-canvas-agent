"""Provider-agnostic model-client interface used by all agents.

Agents pass a normalized request (role + prompt + optional system + optional
image) and never touch a provider SDK directly, so swapping providers is a
config change. `role` selects which configured model id to use.
"""

from typing import Protocol, TypeVar

from pydantic import BaseModel

from ...config import Role

T = TypeVar("T", bound=BaseModel)

# (bytes, mime_type)
Image = tuple[bytes, str]


class ModelError(RuntimeError):
    """Raised when the model provider is unavailable or returns unusable output."""


class ModelClient(Protocol):
    def generate_structured(
        self,
        *,
        role: Role,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        image: Image | None = None,
        temperature: float = 0.2,
    ) -> T: ...

    def generate_text(
        self,
        *,
        role: Role,
        prompt: str,
        system: str | None = None,
        image: Image | None = None,
        temperature: float = 0.4,
    ) -> str: ...
