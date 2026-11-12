"""Application settings.

Values are read (in priority order) from:
1. Environment variables (e.g. APP_NAME=...)
2. A local `.env` file (never committed to Git)
3. The defaults below
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Quiz Generator"
    environment: str = "development"  # development | production


@lru_cache
def get_settings() -> Settings:
    """Return a single cached Settings instance (the .env file is read only once)."""
    return Settings()
