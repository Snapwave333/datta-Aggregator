#!/usr/bin/env python3
"""Run the DaaS Contract Aggregator scraper scheduler."""
import signal
import sys
import time

from src.models.database import init_db
from src.scheduler import scheduler
from src.utils.logger import get_logger

logger = get_logger("main")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal, stopping scheduler...")
    scheduler.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized")

    # Start the scheduler
    print("Starting scraper scheduler...")
    scheduler.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)
            next_run = scheduler.get_next_run()
            if next_run:
                logger.info(f"Next scrape scheduled for: {next_run}")
    except KeyboardInterrupt:
        scheduler.stop()
        sys.exit(0)
