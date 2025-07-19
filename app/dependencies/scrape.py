from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.manage_db import get_async_session
from app.scraping.scraper_service import ScrapingService
from app.telegram.client import TelegramClientWrapper
from app.parsing.llm_parser import SimpleMistralParser
from app.dependencies.repo import get_rental_repository
from app.db.repositories.rental import RentalRepository


def get_telegram_client() -> TelegramClientWrapper:
    """Dependency for Telegram client."""
    return TelegramClientWrapper()


def get_llm_parser() -> SimpleMistralParser:
    """Dependency for LLM parser."""
    return SimpleMistralParser()
