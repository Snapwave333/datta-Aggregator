"""Scraper for SAM.gov (System for Award Management) federal contracts."""
from typing import List, Dict, Any
from datetime import datetime

from src.scrapers.base import PlaywrightScraper
from src.models.contract import ContractStatus
from src.utils.helpers import (
    clean_text,
    parse_date,
    parse_currency,
    extract_email,
    extract_phone,
    generate_external_id,
)


class SAMGovScraper(PlaywrightScraper):
    """Scraper for SAM.gov federal contract opportunities.

    Note: SAM.gov has an official API. This scraper is for demonstration purposes.
    In production, you should use the official API at https://api.sam.gov/opportunities/v2
    """

    def __init__(self, source_id: int):
        """Initialize SAM.gov scraper."""
        super().__init__(
            source_id=source_id,
            source_name="SAM.gov",
            base_url="https://sam.gov",
        )
        self.api_base = "https://api.sam.gov/opportunities/v2/search"

    async def get_listing_urls(self) -> List[str]:
        """Get URLs for contract listings.

        SAM.gov uses a REST API, so we'll construct API request URLs.
        """
        # In a real implementation, you'd paginate through results
        # For demonstration, we'll create several pages worth of URLs
        urls = []
        for page in range(1, 6):  # Get first 5 pages
            urls.append(
                f"{self.api_base}?limit=100&offset={(page-1)*100}&postedFrom=last+30+days"
            )
        return urls

    async def fetch_api_data(self, url: str) -> Dict[str, Any]:
        """Fetch data from SAM.gov API.

        Note: In production, you need an API key from SAM.gov.
        """
        import json
        import aiohttp

        await self._rate_limit()

        headers = {
            "X-Api-Key": "YOUR_SAM_GOV_API_KEY",  # Replace with actual API key
            "Accept": "application/json",
        }

        try:
            self.logger.info(f"Fetching API: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API error: {response.status}")
                        return {"opportunitiesData": []}
        except Exception as e:
            self.logger.error(f"Error fetching API data: {e}")
            return {"opportunitiesData": []}

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse SAM.gov opportunity listing.

        This demonstrates parsing logic for SAM.gov's HTML structure.
        In production, use the API response format.
        """
        contracts = []
        soup = self.parse_html(html)

        # SAM.gov uses dynamic rendering, look for opportunity cards
        opportunity_cards = soup.find_all("div", class_="opportunity-card") or \
                           soup.find_all("div", {"data-testid": "opportunity-result"}) or \
                           soup.find_all("article", class_="opportunity")

        for card in opportunity_cards:
            try:
                contract_data = self._parse_opportunity_card(card)
                if contract_data:
                    contracts.append(contract_data)
            except Exception as e:
                self.logger.error(f"Error parsing opportunity card: {e}")
                continue

        return contracts

    def _parse_opportunity_card(self, card) -> Dict[str, Any]:
        """Parse a single opportunity card from SAM.gov."""
        # Extract notice ID
        notice_id_elem = card.find("span", {"data-testid": "notice-id"}) or \
                         card.find(class_="notice-id")
        notice_id = clean_text(notice_id_elem.text) if notice_id_elem else ""

        if not notice_id:
            return None

        # Extract title
        title_elem = card.find("h2") or card.find("a", class_="opportunity-title")
        title = clean_text(title_elem.text) if title_elem else "Untitled"

        # Extract URL
        url = ""
        if title_elem and title_elem.name == "a":
            url = self.base_url + title_elem.get("href", "")
        elif card.find("a", class_="opportunity-link"):
            url = self.base_url + card.find("a", class_="opportunity-link").get("href", "")

        # Extract agency
        agency_elem = card.find("span", {"data-testid": "agency"}) or \
                      card.find(class_="agency-name")
        agency = clean_text(agency_elem.text) if agency_elem else None

        # Extract dates
        posted_elem = card.find("span", {"data-testid": "posted-date"})
        posted_date = parse_date(posted_elem.text) if posted_elem else None

        due_elem = card.find("span", {"data-testid": "response-deadline"}) or \
                   card.find(class_="due-date")
        due_date = parse_date(due_elem.text) if due_elem else None

        # Extract NAICS code
        naics_elem = card.find("span", {"data-testid": "naics"})
        naics_code = clean_text(naics_elem.text) if naics_elem else None

        # Extract set-aside type
        set_aside_elem = card.find("span", {"data-testid": "set-aside"})
        set_aside = clean_text(set_aside_elem.text) if set_aside_elem else None

        # Extract description
        desc_elem = card.find("div", class_="description") or \
                    card.find("p", class_="opportunity-description")
        description = clean_text(desc_elem.text) if desc_elem else None

        # Determine status
        status = ContractStatus.OPEN
        if due_date and due_date < datetime.utcnow():
            status = ContractStatus.CLOSED

        return {
            "external_id": generate_external_id("sam_gov", notice_id),
            "url": url or f"{self.base_url}/opp/{notice_id}",
            "title": title,
            "description": description,
            "agency": agency,
            "posted_date": posted_date,
            "due_date": due_date,
            "status": status,
            "naics_code": naics_code,
            "set_aside": set_aside,
            "state": "Federal",
            "raw_data": {
                "notice_id": notice_id,
                "source": "SAM.gov",
            },
        }

    async def scrape_from_api(self) -> List[Dict[str, Any]]:
        """Scrape contracts using SAM.gov's official API.

        This is the preferred method for production use.
        """
        contracts = []

        for url in await self.get_listing_urls():
            data = await self.fetch_api_data(url)
            opportunities = data.get("opportunitiesData", [])

            for opp in opportunities:
                contract_data = self._transform_api_response(opp)
                if contract_data:
                    contracts.append(contract_data)

        return contracts

    def _transform_api_response(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Transform SAM.gov API response to contract data."""
        notice_id = opp.get("noticeId", "")

        return {
            "external_id": generate_external_id("sam_gov", notice_id),
            "url": f"{self.base_url}/opp/{notice_id}",
            "title": opp.get("title", ""),
            "description": opp.get("description", ""),
            "agency": opp.get("fullParentPathName", ""),
            "department": opp.get("department", ""),
            "posted_date": parse_date(opp.get("postedDate")),
            "due_date": parse_date(opp.get("responseDeadLine")),
            "status": ContractStatus.OPEN if opp.get("active") else ContractStatus.CLOSED,
            "naics_code": ",".join(opp.get("naicsCode", [])),
            "set_aside": opp.get("typeOfSetAsideDescription", ""),
            "state": "Federal",
            "contact_name": opp.get("primaryContact", {}).get("fullName"),
            "contact_email": opp.get("primaryContact", {}).get("email"),
            "contact_phone": opp.get("primaryContact", {}).get("phone"),
            "raw_data": opp,
        }
