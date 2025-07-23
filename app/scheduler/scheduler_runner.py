import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.scheduler import configure_jobs
from app.core.logger import setup_logging

setup_logging()


async def main():
    scheduler = AsyncIOScheduler()
    configure_jobs(scheduler)
    scheduler.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        raise Exception(f"Failed to run scheduler: {e}") from e
