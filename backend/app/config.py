"""Application configuration (loads `.env` via python-dotenv)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings mapped to `.env` / PRD NFRs."""

    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "sqlite:///./data/processed/shonartalent.db"
        )
    )
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # ML / similarity defaults (FR-3.1, FR-3.3)
    ml_min_matches: int = field(
        default_factory=lambda: int(os.getenv("ML_MIN_MATCHES", "5"))
    )
    similarity_top_k: int = field(
        default_factory=lambda: int(os.getenv("SIMILARITY_TOP_K", "5"))
    )

    # Scrapers: identifies this project honestly to source sites (e.g.
    # Wikipedia's API etiquette asks for a descriptive, contactable
    # User-Agent -- this is the opposite of bot-detection evasion).
    scraper_user_agent: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPER_USER_AGENT", "ShonarTalentAI/0.1 (+contact@example.com)"
        )
    )


settings = Settings()