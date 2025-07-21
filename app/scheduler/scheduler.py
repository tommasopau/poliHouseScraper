import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.dependencies.scrape import get_telegram_client, get_llm_parser
from app.dependencies.repo import get_rental_repository
from app.db.manage_db import get_async_session, async_session
from app.scraping.scraper_service import ScrapingService
logger = logging.getLogger(__name__)


scheduler = AsyncIOScheduler()


async def scrape_job():
    """Simple scraping job - does the main work."""
    logger.info("🚀 Starting scrape job...")

    try:
        # Get what we need
        async with async_session() as db:
            # NOTE we just need one session, when using Depends it already creates just one session
            scraping_service = ScrapingService(
                get_telegram_client(),
                get_llm_parser(),
                get_rental_repository(db)
            )

            # Do the work
            since = datetime.now(timezone.utc) - settings.SCRAPE_SINCE_DELTA
            logger.info(f"Scraping since: {since.isoformat()}")
            results = await scraping_service.scrape_and_process_messages(
                max_messages=100,
                since=since,
            )
            logger.info(f"✅ Scrape job completed: {results}")
            logger.info(f"✅ Job done: {results}")

    except Exception as e:
        logger.error(f"❌ Job failed: {e}")


def start_scheduler():
    """Start the scheduler - keep it simple."""
    if scheduler.running:
        logger.info("Scheduler already running")
        return

    scheduler.add_job(
        scrape_job,
        trigger=IntervalTrigger(minutes=settings.SCRAPE_INTERVAL_MINUTES),
        id="main_scrape_job",
        max_instances=1,  # Don't run multiple at once
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc)
    )

    scheduler.start()
    logger.info(
        f"📅 Scheduler started - running every {settings.SCRAPE_INTERVAL_MINUTES} minutes")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("📅 Scheduler stopped")
