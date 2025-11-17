"""Scheduler for automated scraping jobs."""
import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import settings
from src.models.database import SessionLocal
from src.processors.scrape_manager import ScrapeManager
from src.utils.logger import get_logger

logger = get_logger("scheduler")


class ScraperScheduler:
    """Manages scheduled scraping jobs."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def _scrape_job(self):
        """Execute a scraping job."""
        logger.info("Starting scheduled scraping job...")

        # Create a new database session for this job
        db = SessionLocal()
        try:
            manager = ScrapeManager(db)

            # Run the async scraping in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(manager.scrape_sources_due())

                # Log results
                successful = sum(1 for r in results if r.get("success"))
                total_contracts = sum(r.get("contracts_found", 0) for r in results)

                logger.info(
                    f"Scheduled scrape completed: {successful}/{len(results)} sources successful, "
                    f"{total_contracts} contracts found"
                )

                # Log any errors
                for result in results:
                    if not result.get("success"):
                        logger.error(
                            f"Source {result.get('source_name')} failed: {result.get('error')}"
                        )

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Scraping job failed: {e}")
        finally:
            db.close()

    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Add the scraping job
        self.scheduler.add_job(
            self._scrape_job,
            trigger=IntervalTrigger(minutes=settings.scrape_interval_minutes),
            id="scrape_job",
            name="Scrape all sources",
            replace_existing=True,
        )

        # Start the scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info(
            f"Scheduler started. Scraping every {settings.scrape_interval_minutes} minutes"
        )

        # Run initial scrape
        logger.info("Running initial scrape...")
        self._scrape_job()

    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def run_now(self):
        """Trigger an immediate scrape."""
        logger.info("Triggering immediate scrape...")
        self._scrape_job()

    def get_next_run(self):
        """Get the next scheduled run time."""
        job = self.scheduler.get_job("scrape_job")
        if job:
            return job.next_run_time
        return None


# Global scheduler instance
scheduler = ScraperScheduler()
