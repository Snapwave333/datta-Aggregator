"""Scrapers for state government procurement portals."""
from typing import List, Dict, Any
from datetime import datetime

from src.scrapers.base import BaseScraper, PlaywrightScraper
from src.models.contract import ContractStatus
from src.utils.helpers import (
    clean_text,
    parse_date,
    parse_currency,
    extract_email,
    extract_phone,
    generate_external_id,
)


class CaliforniaScraper(PlaywrightScraper):
    """Scraper for California State Contracts Register (Cal eProcure)."""

    def __init__(self, source_id: int):
        """Initialize California scraper."""
        super().__init__(
            source_id=source_id,
            source_name="California_eProcure",
            base_url="https://caleprocure.ca.gov",
        )

    async def get_listing_urls(self) -> List[str]:
        """Get URLs for California procurement listings."""
        # Cal eProcure search pages
        urls = [
            f"{self.base_url}/pages/BidSearch/BidSearch.aspx?PageIndex={i}"
            for i in range(1, 11)  # First 10 pages
        ]
        return urls

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse California procurement listing page."""
        contracts = []
        soup = self.parse_html(html)

        # Find bid table
        bid_table = soup.find("table", {"id": "BidSearchResults"}) or \
                    soup.find("table", class_="bid-list")

        if not bid_table:
            return contracts

        rows = bid_table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            try:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                contract_data = self._parse_row(cols)
                if contract_data:
                    contracts.append(contract_data)
            except Exception as e:
                self.logger.error(f"Error parsing row: {e}")
                continue

        return contracts

    def _parse_row(self, cols) -> Dict[str, Any]:
        """Parse a single row from the bid table."""
        # Extract bid number
        bid_num_elem = cols[0].find("a")
        bid_number = clean_text(bid_num_elem.text) if bid_num_elem else ""

        if not bid_number:
            return None

        # Extract URL
        url = ""
        if bid_num_elem and bid_num_elem.get("href"):
            href = bid_num_elem.get("href")
            url = href if href.startswith("http") else f"{self.base_url}{href}"

        # Extract title
        title = clean_text(cols[1].text) if len(cols) > 1 else "Untitled"

        # Extract agency
        agency = clean_text(cols[2].text) if len(cols) > 2 else None

        # Extract dates
        posted_date = parse_date(cols[3].text) if len(cols) > 3 else None
        due_date = parse_date(cols[4].text) if len(cols) > 4 else None

        # Determine status
        status = ContractStatus.OPEN
        if due_date and due_date < datetime.utcnow():
            status = ContractStatus.CLOSED

        # Extract estimated value if present
        estimated_value = None
        if len(cols) > 5:
            estimated_value = parse_currency(cols[5].text)

        return {
            "external_id": generate_external_id("ca_eprocure", bid_number),
            "url": url,
            "title": title,
            "agency": agency,
            "posted_date": posted_date,
            "due_date": due_date,
            "status": status,
            "estimated_value": estimated_value,
            "state": "California",
            "raw_data": {
                "bid_number": bid_number,
                "source": "Cal eProcure",
            },
        }


class TexasScraper(BaseScraper):
    """Scraper for Texas Electronic State Business Daily (ESBD)."""

    def __init__(self, source_id: int):
        """Initialize Texas scraper."""
        super().__init__(
            source_id=source_id,
            source_name="Texas_ESBD",
            base_url="https://www.txsmartbuy.gov",
        )

    async def get_listing_urls(self) -> List[str]:
        """Get URLs for Texas ESBD listings."""
        # Texas SmartBuy search pages
        urls = [
            f"{self.base_url}/sp?page={i}"
            for i in range(1, 11)  # First 10 pages
        ]
        return urls

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse Texas ESBD listing page."""
        contracts = []
        soup = self.parse_html(html)

        # Find opportunity listings
        listings = soup.find_all("div", class_="opportunity-item") or \
                   soup.find_all("tr", class_="bid-row")

        for listing in listings:
            try:
                contract_data = self._parse_listing(listing)
                if contract_data:
                    contracts.append(contract_data)
            except Exception as e:
                self.logger.error(f"Error parsing listing: {e}")
                continue

        return contracts

    def _parse_listing(self, listing) -> Dict[str, Any]:
        """Parse a single listing from Texas ESBD."""
        # Extract solicitation number
        sol_num_elem = listing.find("span", class_="solicitation-number") or \
                       listing.find("td", class_="sol-num")
        sol_number = clean_text(sol_num_elem.text) if sol_num_elem else ""

        if not sol_number:
            return None

        # Extract title
        title_elem = listing.find("h3") or listing.find("a", class_="title-link")
        title = clean_text(title_elem.text) if title_elem else "Untitled"

        # Extract URL
        url = ""
        if title_elem and title_elem.name == "a":
            url = self.base_url + title_elem.get("href", "")

        # Extract agency
        agency_elem = listing.find("span", class_="agency")
        agency = clean_text(agency_elem.text) if agency_elem else None

        # Extract description
        desc_elem = listing.find("div", class_="description") or \
                    listing.find("p", class_="summary")
        description = clean_text(desc_elem.text) if desc_elem else None

        # Extract dates
        posted_elem = listing.find("span", class_="posted-date")
        posted_date = parse_date(posted_elem.text) if posted_elem else None

        due_elem = listing.find("span", class_="due-date") or \
                   listing.find("span", class_="closing-date")
        due_date = parse_date(due_elem.text) if due_elem else None

        # Extract category
        category_elem = listing.find("span", class_="category")
        category = clean_text(category_elem.text) if category_elem else None

        # Extract estimated value
        value_elem = listing.find("span", class_="estimated-value")
        estimated_value = parse_currency(value_elem.text) if value_elem else None

        # Determine status
        status = ContractStatus.OPEN
        if due_date and due_date < datetime.utcnow():
            status = ContractStatus.CLOSED

        return {
            "external_id": generate_external_id("tx_esbd", sol_number),
            "url": url,
            "title": title,
            "description": description,
            "agency": agency,
            "category": category,
            "posted_date": posted_date,
            "due_date": due_date,
            "estimated_value": estimated_value,
            "status": status,
            "state": "Texas",
            "raw_data": {
                "solicitation_number": sol_number,
                "source": "Texas ESBD",
            },
        }


class NewYorkScraper(PlaywrightScraper):
    """Scraper for New York State Contract Reporter."""

    def __init__(self, source_id: int):
        """Initialize New York scraper."""
        super().__init__(
            source_id=source_id,
            source_name="NewYork_ContractReporter",
            base_url="https://www.nyscr.ny.gov",
        )

    async def get_listing_urls(self) -> List[str]:
        """Get URLs for New York Contract Reporter listings."""
        # NY Contract Reporter search pages
        urls = [
            f"{self.base_url}/adsOpen.cfm?startRow={i*20}"
            for i in range(10)  # First 10 pages (20 results per page)
        ]
        return urls

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse New York Contract Reporter listing page."""
        contracts = []
        soup = self.parse_html(html)

        # Find advertisement listings
        ads = soup.find_all("div", class_="advertisement") or \
              soup.find_all("div", class_="contract-listing")

        for ad in ads:
            try:
                contract_data = self._parse_advertisement(ad)
                if contract_data:
                    contracts.append(contract_data)
            except Exception as e:
                self.logger.error(f"Error parsing advertisement: {e}")
                continue

        return contracts

    def _parse_advertisement(self, ad) -> Dict[str, Any]:
        """Parse a single advertisement from NY Contract Reporter."""
        # Extract ad number
        ad_num_elem = ad.find("span", class_="ad-number")
        ad_number = clean_text(ad_num_elem.text) if ad_num_elem else ""

        if not ad_number:
            return None

        # Extract title
        title_elem = ad.find("h2") or ad.find("div", class_="title")
        title = clean_text(title_elem.text) if title_elem else "Untitled"

        # Extract URL
        url_elem = ad.find("a", class_="detail-link")
        url = ""
        if url_elem:
            href = url_elem.get("href", "")
            url = href if href.startswith("http") else f"{self.base_url}/{href}"

        # Extract agency
        agency_elem = ad.find("div", class_="agency") or \
                      ad.find("span", class_="contracting-agency")
        agency = clean_text(agency_elem.text) if agency_elem else None

        # Extract description
        desc_elem = ad.find("div", class_="description")
        description = clean_text(desc_elem.text) if desc_elem else None

        # Extract dates
        posted_elem = ad.find("span", class_="publication-date")
        posted_date = parse_date(posted_elem.text) if posted_elem else None

        due_elem = ad.find("span", class_="due-date")
        due_date = parse_date(due_elem.text) if due_elem else None

        # Extract contract type
        type_elem = ad.find("span", class_="contract-type")
        category = clean_text(type_elem.text) if type_elem else None

        # Extract estimated amount
        amount_elem = ad.find("span", class_="estimated-amount")
        estimated_value = parse_currency(amount_elem.text) if amount_elem else None

        # Extract contact information
        contact_elem = ad.find("div", class_="contact-info")
        contact_text = contact_elem.text if contact_elem else ""
        contact_name = None
        contact_email = extract_email(contact_text)
        contact_phone = extract_phone(contact_text)

        # Try to extract name from first line
        if contact_elem:
            name_elem = contact_elem.find("span", class_="contact-name")
            if name_elem:
                contact_name = clean_text(name_elem.text)

        # Determine status
        status = ContractStatus.OPEN
        if due_date and due_date < datetime.utcnow():
            status = ContractStatus.CLOSED

        return {
            "external_id": generate_external_id("ny_cr", ad_number),
            "url": url,
            "title": title,
            "description": description,
            "agency": agency,
            "category": category,
            "posted_date": posted_date,
            "due_date": due_date,
            "estimated_value": estimated_value,
            "status": status,
            "state": "New York",
            "city": "Albany",  # State contracts typically based in Albany
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "raw_data": {
                "advertisement_number": ad_number,
                "source": "NY Contract Reporter",
            },
        }
