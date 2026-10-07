import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    openrouter_max_tokens: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    max_upload_bytes: int = 5 * 1024 * 1024
    max_resume_characters: int = 100_000


settings = Settings()

