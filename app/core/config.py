"""
Pydantic settings for environment configuration.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database
    DATABASE_URL: str
    DATABASE_URL_SUPABASE: str

    PORT: int

    # Telegram API
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: str
    TELEGRAM_SESSION_NAME: str = "house_scraper"
    TELEGRAM_SESSION_STRING: str

    # LLM Configuration
    MISTRAL_API_KEY: str

    # Scheduler
    SCRAPE_INTERVAL_MINUTES: int = 60
    SCRAPE_SINCE_DELTA: timedelta = timedelta(minutes=60)

    CHANNEL_NAME: str = "@polihouse"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
