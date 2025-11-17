"""Base scraper classes with rate limiting and error handling."""
import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.logger import get_logger
from src.models.contract import Contract


class BaseScraper(ABC):
    """Base scraper class for static websites."""

    def __init__(self, source_id: int, source_name: str, base_url: str):
        """Initialize the scraper."""
        self.source_id = source_id
        self.source_name = source_name
        self.base_url = base_url
        self.logger = get_logger(f"scraper.{source_name}")
        self.ua = UserAgent()
        self.session = requests.Session()
        self.rate_limit_delay = settings.rate_limit_delay_seconds
        self._last_request_time = 0

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random user agent."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

    async def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)

        self._last_request_time = asyncio.get_event_loop().time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with rate limiting and retries."""
        await self._rate_limit()

        try:
            self.logger.info(f"Fetching: {url}")
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=settings.request_timeout_seconds,
                ),
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def get_listing_urls(self) -> List[str]:
        """Get URLs of pages containing contract listings."""
        pass

    @abstractmethod
    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse a listing page to extract contract data."""
        pass

    def create_contract_from_data(self, data: Dict[str, Any]) -> Contract:
        """Create a Contract object from scraped data."""
        contract = Contract(
            external_id=data.get("external_id", ""),
            source_id=self.source_id,
            url=data.get("url", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            agency=data.get("agency"),
            department=data.get("department"),
            budget_min=data.get("budget_min"),
            budget_max=data.get("budget_max"),
            estimated_value=data.get("estimated_value"),
            posted_date=data.get("posted_date"),
            due_date=data.get("due_date"),
            close_date=data.get("close_date"),
            status=data.get("status"),
            category=data.get("category"),
            naics_code=data.get("naics_code"),
            set_aside=data.get("set_aside"),
            state=data.get("state"),
            city=data.get("city"),
            zip_code=data.get("zip_code"),
            contact_name=data.get("contact_name"),
            contact_email=data.get("contact_email"),
            contact_phone=data.get("contact_phone"),
            raw_data=json.dumps(data.get("raw_data", {})),
            last_scraped_at=datetime.utcnow(),
        )
        return contract

    async def scrape(self) -> List[Contract]:
        """Main scraping method."""
        contracts = []

        try:
            # Get listing URLs
            listing_urls = await self.get_listing_urls()
            self.logger.info(f"Found {len(listing_urls)} listing pages to scrape")

            # Scrape each listing page
            for url in listing_urls:
                try:
                    html = await self.fetch_page(url)
                    if html:
                        page_contracts = await self.parse_listing_page(html)
                        for contract_data in page_contracts:
                            contract = self.create_contract_from_data(contract_data)
                            contracts.append(contract)
                        self.logger.info(
                            f"Extracted {len(page_contracts)} contracts from {url}"
                        )
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    continue

            self.logger.info(f"Total contracts scraped: {len(contracts)}")
            return contracts

        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise


class PlaywrightScraper(BaseScraper):
    """Scraper for JavaScript-heavy websites using Playwright."""

    def __init__(self, source_id: int, source_name: str, base_url: str):
        """Initialize the Playwright scraper."""
        super().__init__(source_id, source_name, base_url)
        self.browser = None
        self.context = None

    async def init_browser(self):
        """Initialize Playwright browser."""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent=self.ua.random,
            viewport={"width": 1920, "height": 1080},
        )

    async def close_browser(self):
        """Close Playwright browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page using Playwright."""
        await self._rate_limit()

        if not self.browser:
            await self.init_browser()

        try:
            self.logger.info(f"Fetching (JS): {url}")
            page = await self.context.new_page()
            await page.goto(url, timeout=settings.request_timeout_seconds * 1000)
            await page.wait_for_load_state("networkidle")

            # Give time for any JavaScript to finish
            await asyncio.sleep(1)

            content = await page.content()
            await page.close()
            return content

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise

    async def scrape(self) -> List[Contract]:
        """Main scraping method with browser lifecycle management."""
        try:
            await self.init_browser()
            contracts = await super().scrape()
            return contracts
        finally:
            await self.close_browser()
