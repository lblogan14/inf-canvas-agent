"""Application settings, loaded from the repo-root `.env`."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""

    # Gemini model ids per agent role.
    gemini_model_pro: str = "gemini-2.5-pro"
    gemini_model_flash: str = "gemini-2.5-flash"
    # Vision/extraction benefits most from the newest spatial-grounding model.
    gemini_model_vision: str = "gemini-3-pro"

    storage_dir: str = "storage"
    frontend_origin: str = "http://localhost:5173"

    @property
    def storage_path(self) -> Path:
        path = BACKEND_DIR / self.storage_dir
        return path

    @property
    def projects_path(self) -> Path:
        return self.storage_path / "projects"

    @property
    def uploads_path(self) -> Path:
        return self.storage_path / "uploads"

    @property
    def has_api_key(self) -> bool:
        return bool(self.google_api_key)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.projects_path.mkdir(parents=True, exist_ok=True)
    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    return settings
