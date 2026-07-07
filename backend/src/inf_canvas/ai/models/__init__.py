"""Model clients. Gemini is the default provider; any other provider is served
through LangChain. `get_model_client()` picks based on `LLM_PROVIDER`.
"""

from functools import lru_cache

from ...config import get_settings
from .base import ModelClient, ModelError
from .gemini import GeminiClient

__all__ = ["ModelClient", "ModelError", "get_model_client"]


@lru_cache
def get_model_client() -> ModelClient:
    """Cached client for the configured provider. Raises ModelError if unusable."""
    settings = get_settings()
    if settings.is_gemini:
        return GeminiClient(settings)
    from .langchain_client import LangChainClient

    return LangChainClient(settings)
