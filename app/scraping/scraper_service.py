"""
Main scraping service that orchestrates the entire scraping pipeline.
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta, date

from app.telegram.client import TelegramClientWrapper
from app.parsing.llm_parser import SimpleMistralParser
from app.db.repositories.rental import RentalRepository
from app.db.models import Rental, TelegramMessageData
import asyncio

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Main service that orchestrates telegram scraping, LLM parsing, and database storage.
    """

    def __init__(
        self,
        telegram_client: TelegramClientWrapper,
        llm_parser: SimpleMistralParser,
        rental_repository: RentalRepository
    ):
        self.telegram_client = telegram_client
        self.llm_parser = llm_parser
        self.rental_repository = rental_repository

    async def scrape_and_process_messages(
        self,
        since: Optional[datetime] = None,
        max_messages: int = 50
    ) -> dict:
        """
        Complete scraping pipeline: fetch -> parse -> store.

        Returns:
            dict: Summary of processing results
        """
        results = {
            "messages_fetched": 0,
            "messages_parsed": 0,
            "messages_saved": 0,
            "errors": []
        }

        try:
            # Step 1: Fetch messages from Telegram
            logger.info("Starting message scraping...")
            messages = await self._fetch_messages(since, max_messages)
            results["messages_fetched"] = len(messages)

            if not messages:
                logger.info("No new messages found")
                return results

            # Step 2: Parse messages with LLM
            logger.info(f"Parsing {len(messages)} messages...")
            parsed_data = await self._parse_messages(messages)
            results["messages_parsed"] = len(parsed_data)

            # Step 3: Save to database
            logger.info("Saving to database...")
            saved_count = await self._save_rentals(parsed_data)
            results["messages_saved"] = saved_count

            logger.info(f"Scraping completed: {results}")
            return results

        except Exception as e:
            error_msg = f"Scraping pipeline failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results

    async def _fetch_messages(
        self,
        since: Optional[datetime],
        max_messages: int
    ) -> List[TelegramMessageData]:
        """Fetch messages from Telegram."""
        try:
            await self.telegram_client.connect()
            messages = await self.telegram_client.fetch_new_messages(since)

            # Limit messages to avoid overwhelming the LLM API
            if len(messages) > max_messages:
                logger.warning(
                    f"Limiting messages from {len(messages)} to {max_messages}")
                messages = messages[:max_messages]

            return messages

        except Exception as e:
            logger.error(f"Failed to fetch messages: {e}")
            raise
        finally:
            await self.telegram_client.disconnect()

    async def _parse_messages(
        self,
        messages: List[TelegramMessageData]
    ) -> List[dict]:
        """Parse messages using LLM."""
        parsed_data = []

        for i, message in enumerate(messages):
            try:
                # Add delay to respect rate limits
                if i > 0:
                    await asyncio.sleep(1.5)  # 2 seconds between calls

                parsed = await self.llm_parser.parse_message(message)
                parsed_data.append(parsed)

            except Exception as e:
                logger.error(f"Failed to parse message {message.id}: {e}")
                # Continue with other messages
                continue

        return parsed_data

    async def _save_rentals(self, parsed_data: List[dict]) -> int:
        """Save parsed data to database."""
        saved_count = 0

        for data in parsed_data:
            try:
                rental = self._create_rental_from_data(
                    data
                )

                # Check if already exists
                existing = await self._check_duplicate(rental)
                if existing:
                    logger.debug(
                        f"Skipping duplicate message {rental.telegram_message_id}")
                    continue

                await self.rental_repository.create(rental)
                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save rental: {e}")
                continue

        return saved_count

    def _create_rental_from_data(
        self,
        parsed: dict
    ) -> Rental:
        """Create Rental model from message and parsed data."""
        message_date = parsed.get("date")
        if message_date and hasattr(message_date, "tzinfo") and message_date.tzinfo is not None:
            message_date = message_date.replace(tzinfo=None)
        return Rental(
            telegram_message_id=parsed.get(
                "message_id"),
            sender_id=parsed.get("sender_id"),
            sender_username=parsed.get("sender_username"),
            message_date=message_date,
            raw_text=parsed.get("raw_text", ""),
            summary=parsed.get("summary"),
            price=parsed.get("price"),
            location=parsed.get("location"),
            property_type=parsed.get("property_type"),
            telephone=parsed.get("telephone"),
            email=parsed.get("email"),
            tenant_preference=parsed.get("tenant_preference"),
            num_bedrooms=parsed.get("num_bedrooms"),
            num_bathrooms=parsed.get("num_bathrooms"),
            flatmates_count=parsed.get("flatmates_count"),
            # Convert date strings to date objects if needed
            availability_start=self._parse_date(parsed.get("available_start")),
            availability_end=self._parse_date(parsed.get("available_end"))
        )

    async def _check_duplicate(self, rental: Rental) -> bool:
        """Check if rental already exists in database."""
        if rental.telegram_message_id:
            # Add method to repository to check by telegram_message_id
            existing = await self.rental_repository.find_by_telegram_id(
                rental.telegram_message_id
            )
            return existing is not None
        return False

    def _parse_date(date_str: str) -> Optional[date]:
        """
        Parse a date string in 'YY-MM-DD' or 'YYYY-MM-DD' format to a date object.
        """
        for fmt in ("%y-%m-%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
