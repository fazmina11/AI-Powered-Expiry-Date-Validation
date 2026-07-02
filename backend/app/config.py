"""
config.py — Centralised application settings.

All values are loaded from environment variables (or a .env file).
No hardcoded secrets or database URLs anywhere in the codebase.

Usage:
    from app.config import settings
    settings.DATABASE_URL
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./expiry_validation.db"

    # Security
    SECRET_KEY: str = "change_this_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Shelf-life decision thresholds (days)
    WARNING_DAYS: int = 60   # remaining_days <= WARNING_DAYS → PRIORITY_SALE
    REJECT_DAYS: int = 30    # remaining_days < REJECT_DAYS  → REJECTED

    # Runtime environment
    APP_ENV: str = "development"  # development | staging | production

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
