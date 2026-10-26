"""Application settings, loaded once from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "gpt-6-astra"
DEFAULT_ITEMS_PER_PAGE = 10
LOG_PATH = PROJECT_ROOT / "data" / "cli-chat.log"
load_dotenv(PROJECT_ROOT / ".env")


class ConfigError(Exception):
    """The application is not configured correctly."""


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    model: str
    db_path: Path
    items_per_page: int


@lru_cache
def get_settings() -> Settings:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError("OPENAI_API_KEY is missing. Copy .env.example to .env and set your key.")
    return Settings(
        openai_api_key=api_key,
        model=os.getenv("OPENAI_MODEL") or DEFAULT_MODEL,
        db_path=Path(os.getenv("CHAT_DB_PATH") or PROJECT_ROOT / "data" / "chat.db"),
        items_per_page=int(os.getenv("ITEMS_PER_PAGE") or DEFAULT_ITEMS_PER_PAGE),
    )
