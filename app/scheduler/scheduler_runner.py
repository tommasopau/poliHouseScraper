import asyncio
from app.scheduler.scheduler import start_scheduler
from app.core.logger import setup_logging

setup_logging()

if __name__ == "__main__":
    start_scheduler()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Scheduler stopped.")
    except Exception as e:
        raise Exception(f"Failed to fetch messages: {e}") from e
