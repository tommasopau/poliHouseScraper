from telethon import TelegramClient
from telethon.sessions import StringSession
from app.core.config import settings
import asyncio

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH


async def main():
    client = TelegramClient(settings.TELEGRAM_SESSION_NAME, api_id, api_hash)
    await client.start()
    print(StringSession.save(client.session))
    await client.disconnect()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
