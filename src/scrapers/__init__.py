"""Scrapers for DaaS Contract Aggregator."""
from src.scrapers.base import BaseScraper, PlaywrightScraper
from src.scrapers.sam_gov import SAMGovScraper
from src.scrapers.state_portals import CaliforniaScraper, TexasScraper, NewYorkScraper

__all__ = [
    "BaseScraper",
    "PlaywrightScraper",
    "SAMGovScraper",
    "CaliforniaScraper",
    "TexasScraper",
    "NewYorkScraper",
]

# Registry of available scrapers
SCRAPER_REGISTRY = {
    "SAMGovScraper": SAMGovScraper,
    "CaliforniaScraper": CaliforniaScraper,
    "TexasScraper": TexasScraper,
    "NewYorkScraper": NewYorkScraper,
}
