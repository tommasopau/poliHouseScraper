"""
Telegram client wrapper using Telethon.
"""
from typing import List, Optional, AsyncGenerator
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from telethon import TelegramClient
from telethon.tl.types import Message
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError, FloodWaitError
from app.core.config import settings
from app.db.models import TelegramMessageData


class TelegramClientWrapper:
    """
    Wrapper around Telethon client for scraping rental messages.
    """

    def __init__(self):
        """Initialize Telegram client."""
        self.client = TelegramClient(
            settings.TELEGRAM_SESSION_NAME,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH
        )
        self._is_connected = False
        self.channel_name = settings.CHANNEL_NAME

    async def connect(self) -> None:
        """
        Connect to Telegram and authenticate.
        """
        try:
            await self.client.start(phone=settings.TELEGRAM_PHONE)
            self._is_connected = True
        except Exception as e:
            raise NotImplementedError(f"Authentication failed: {e}")

    async def disconnect(self) -> None:
        """
        Disconnect from Telegram.
        """
        if self._is_connected:
            await self.client.disconnect()
            self._is_connected = False

    async def fetch_new_messages(
        self,
        since: Optional[datetime] = None
    ) -> List[TelegramMessageData]:
        """
        Fetch new messages from a channel since given datetime.

        Args:
            since: Fetch messages since this datetime (default: last hour)

        Returns:
            List[Message]: List of Telegram message objects for batch processing
        """
        if not self._is_connected:
            await self.connect()

        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=1)

        try:
            messages_count = 0
            messages = []
            # async for because Telethon's iter_messages is async generator
            async for message in self.client.iter_messages(
                self.channel_name,
                limit=None
            ):

                if message.date and message.date < since:
                    break
                if message.text and self._is_rental_message(message.text):
                    messages_count += 1
                    messages.append(self._extract_message_data(message))

            return messages

        except ChannelPrivateError:
            raise Exception(
                f"Cannot access private channel: {self.channel_name}")
        except UsernameNotOccupiedError:
            raise Exception(f"Channel not found: {self.channel_name}")
        except FloodWaitError as e:
            raise Exception(f"Rate limited. Wait {e.seconds} seconds")
        except Exception as e:
            raise Exception(f"Failed to fetch messages: {e}")

    def _extract_message_data(self, message: Message) -> TelegramMessageData:
        """        Extract relevant data from a Telegram message.
        Args:
            message: Telegram message object
        Returns:
            dict: Extracted data from the message
        """
        return TelegramMessageData(
            id=message.id,
            text=message.text,
            date=message.date,
            sender_id=getattr(message.sender, 'id',
                              None) if message.sender else None,
            sender_username=getattr(
                message.sender, 'username', None) if message.sender else None,
            has_media=bool(message.media)
        )

    def _is_rental_message(self, text: str) -> bool:
        """
        Basic filtering to identify potential rental messages.

        Args:
            text: Message text

        Returns:
            bool: True if message might be a rental listing
        """

        rental_keywords = ["#offro", "offered", "offro"]
        text_lower = text.lower()
        if text_lower.startswith("#offro"):
            return True
        return any(keyword in text_lower for keyword in rental_keywords)
