"""Application settings, loaded from the repo-root `.env`."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent

Role = Literal["pro", "flash", "vision"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM provider (default Gemini, but any provider works) --------------
    # "gemini" uses the google-genai SDK directly. Any other value (e.g.
    # "openai", "anthropic", "google_genai", "groq", ...) routes through
    # LangChain's init_chat_model — install the `providers` extra for those.
    llm_provider: str = "gemini"

    # Model ids per agent role. `MODEL_*` are the provider-agnostic names;
    # the legacy `GEMINI_MODEL_*` names still work for the Gemini provider.
    pro_model: str = Field(
        default="gemini-2.5-pro",
        validation_alias=AliasChoices("MODEL_PRO", "GEMINI_MODEL_PRO", "pro_model"),
    )
    flash_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("MODEL_FLASH", "GEMINI_MODEL_FLASH", "flash_model"),
    )
    vision_model: str = Field(
        default="gemini-3.1-pro-preview",
        validation_alias=AliasChoices("MODEL_VISION", "GEMINI_MODEL_VISION", "vision_model"),
    )

    # API keys. Gemini needs GOOGLE_API_KEY; other providers read their own
    # env var (OPENAI_API_KEY, ANTHROPIC_API_KEY, ...) via LangChain.
    google_api_key: str = ""

    storage_dir: str = "storage"
    frontend_origin: str = "http://localhost:5173"

    # P&ID extractor accuracy passes (extra latency/cost; disable for speed).
    extractor_verify: bool = True  # Set-of-Mark verifier pass
    extractor_line_hybrid: bool = True  # OpenCV line-connection proposals

    def model_id(self, role: Role) -> str:
        return {"pro": self.pro_model, "flash": self.flash_model, "vision": self.vision_model}[role]

    @property
    def storage_path(self) -> Path:
        return BACKEND_DIR / self.storage_dir

    @property
    def projects_path(self) -> Path:
        return self.storage_path / "projects"

    @property
    def uploads_path(self) -> Path:
        return self.storage_path / "uploads"

    @property
    def is_gemini(self) -> bool:
        return self.llm_provider == "gemini"

    @property
    def has_api_key(self) -> bool:
        # Only the Gemini provider is validated here; other providers rely on
        # their own SDK env vars, checked lazily when the client is built.
        return not self.is_gemini or bool(self.google_api_key)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.projects_path.mkdir(parents=True, exist_ok=True)
    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    return settings
