"""Helper functions for data processing."""
import re
from datetime import datetime
from typing import Optional
from dateutil import parser as date_parser


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and normalize text."""
    if not text:
        return None

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove control characters
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

    return text.strip() if text else None


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_string:
        return None

    try:
        # Try to parse with dateutil
        return date_parser.parse(date_string, fuzzy=True)
    except (ValueError, TypeError):
        return None


def parse_currency(amount_string: Optional[str]) -> Optional[float]:
    """Parse currency string to float."""
    if not amount_string:
        return None

    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r"[^\d.]", "", str(amount_string))
        if cleaned:
            return float(cleaned)
    except (ValueError, TypeError):
        pass

    return None


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    if not text:
        return None

    # Simple email regex
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    if not text:
        return None

    # US phone number patterns
    patterns = [
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\d{3}[-.\s]\d{3}[-.\s]\d{4}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return None


def generate_external_id(source_name: str, *identifiers) -> str:
    """Generate a unique external ID for a contract."""
    parts = [source_name] + [str(id_part) for id_part in identifiers if id_part]
    return "_".join(parts)
