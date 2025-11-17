"""Scrape manager for coordinating scraping operations."""
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from src.models.source import DataSource, SourceStatus
from src.scrapers import SCRAPER_REGISTRY
from src.processors.aggregator import ContractAggregator
from src.utils.logger import get_logger
from src.config import settings

logger = get_logger("scrape_manager")


class ScrapeManager:
    """Manages and coordinates scraping operations across multiple sources."""

    def __init__(self, db: Session):
        """Initialize the scrape manager."""
        self.db = db
        self.aggregator = ContractAggregator(db)
        self.max_concurrent = settings.max_concurrent_scrapers

    async def scrape_source(self, source: DataSource) -> Dict[str, Any]:
        """Scrape a single data source."""
        logger.info(f"Starting scrape for: {source.name}")

        result = {
            "source_id": source.id,
            "source_name": source.name,
            "success": False,
            "contracts_found": 0,
            "stats": {},
            "error": None,
        }

        try:
            # Mark source as being scraped
            source.last_scrape_at = datetime.utcnow()
            self.db.commit()

            # Get scraper class
            scraper_class = SCRAPER_REGISTRY.get(source.scraper_class)
            if not scraper_class:
                raise ValueError(f"Unknown scraper class: {source.scraper_class}")

            # Initialize scraper
            scraper = scraper_class(source.id)
            scraper.rate_limit_delay = source.rate_limit_seconds

            # Run scraping
            contracts = await scraper.scrape()

            # Aggregate results
            stats = self.aggregator.save_contracts(contracts, source)

            # Update result
            result["success"] = True
            result["contracts_found"] = len(contracts)
            result["stats"] = stats

            # Update source status
            source.status = SourceStatus.ACTIVE
            source.last_error = None
            self.db.commit()

            logger.info(f"Completed scrape for {source.name}: {len(contracts)} contracts found")

        except Exception as e:
            logger.error(f"Error scraping {source.name}: {e}")

            # Update source with error
            source.status = SourceStatus.ERROR
            source.last_error = str(e)

            # Update success rate
            if source.total_scrapes > 0:
                # Simple moving average
                source.success_rate = int(
                    (source.success_rate * source.total_scrapes) / (source.total_scrapes + 1)
                )

            self.db.commit()

            result["error"] = str(e)

        return result

    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all active data sources."""
        sources = (
            self.db.query(DataSource)
            .filter(DataSource.status == SourceStatus.ACTIVE)
            .all()
        )

        logger.info(f"Starting scrape for {len(sources)} active sources")

        results = []

        # Process sources with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def scrape_with_semaphore(source):
            async with semaphore:
                return await self.scrape_source(source)

        # Create tasks
        tasks = [scrape_with_semaphore(source) for source in sources]

        # Run all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    "source_id": sources[i].id if i < len(sources) else None,
                    "source_name": sources[i].name if i < len(sources) else "Unknown",
                    "success": False,
                    "error": str(result),
                })
            else:
                final_results.append(result)

        # Summary
        successful = sum(1 for r in final_results if r.get("success"))
        total_contracts = sum(r.get("contracts_found", 0) for r in final_results)

        logger.info(
            f"Scraping complete: {successful}/{len(sources)} sources successful, "
            f"{total_contracts} total contracts found"
        )

        return final_results

    async def scrape_sources_due(self) -> List[Dict[str, Any]]:
        """Scrape only sources that are due for a refresh."""
        from datetime import timedelta

        now = datetime.utcnow()
        results = []

        # Get all active sources
        sources = (
            self.db.query(DataSource)
            .filter(DataSource.status == SourceStatus.ACTIVE)
            .all()
        )

        # Filter sources that are due
        due_sources = []
        for source in sources:
            if source.last_scrape_at is None:
                # Never scraped, scrape now
                due_sources.append(source)
            else:
                # Check if enough time has passed
                next_scrape = source.last_scrape_at + timedelta(
                    minutes=source.scrape_frequency_minutes
                )
                if now >= next_scrape:
                    due_sources.append(source)

        if not due_sources:
            logger.info("No sources due for scraping")
            return results

        logger.info(f"{len(due_sources)} sources due for scraping")

        # Scrape due sources
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def scrape_with_semaphore(source):
            async with semaphore:
                return await self.scrape_source(source)

        tasks = [scrape_with_semaphore(source) for source in due_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    "source_id": due_sources[i].id if i < len(due_sources) else None,
                    "source_name": due_sources[i].name if i < len(due_sources) else "Unknown",
                    "success": False,
                    "error": str(result),
                })
            else:
                final_results.append(result)

        return final_results

    def add_source(
        self,
        name: str,
        base_url: str,
        scraper_class: str,
        **kwargs
    ) -> DataSource:
        """Add a new data source."""
        source = DataSource(
            name=name,
            base_url=base_url,
            scraper_class=scraper_class,
            **kwargs
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)

        logger.info(f"Added new source: {name}")
        return source

    def get_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all data sources."""
        sources = self.db.query(DataSource).all()
        return [source.to_dict() for source in sources]
