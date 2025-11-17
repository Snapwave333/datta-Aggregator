"""Tests for helper functions."""
import pytest
from datetime import datetime
from src.utils.helpers import (
    clean_text,
    parse_date,
    parse_currency,
    extract_email,
    extract_phone,
    generate_external_id,
)


class TestCleanText:
    """Tests for clean_text function."""

    def test_removes_extra_whitespace(self):
        assert clean_text("  hello   world  ") == "hello world"

    def test_handles_none(self):
        assert clean_text(None) is None

    def test_handles_empty_string(self):
        assert clean_text("") is None

    def test_removes_control_characters(self):
        text = "hello\x00world"
        result = clean_text(text)
        assert "\x00" not in result


class TestParseDate:
    """Tests for parse_date function."""

    def test_parses_standard_date(self):
        result = parse_date("2024-01-15")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parses_us_format(self):
        result = parse_date("01/15/2024")
        assert result is not None
        assert result.year == 2024

    def test_handles_none(self):
        assert parse_date(None) is None

    def test_handles_invalid_date(self):
        assert parse_date("not a date") is None


class TestParseCurrency:
    """Tests for parse_currency function."""

    def test_parses_simple_number(self):
        assert parse_currency("1000") == 1000.0

    def test_parses_with_dollar_sign(self):
        assert parse_currency("$1,500.00") == 1500.0

    def test_parses_with_commas(self):
        assert parse_currency("1,000,000") == 1000000.0

    def test_handles_none(self):
        assert parse_currency(None) is None

    def test_handles_invalid_input(self):
        assert parse_currency("not a number") is None


class TestExtractEmail:
    """Tests for extract_email function."""

    def test_extracts_email(self):
        text = "Contact: john.doe@example.com for more info"
        assert extract_email(text) == "john.doe@example.com"

    def test_handles_no_email(self):
        assert extract_email("No email here") is None

    def test_handles_none(self):
        assert extract_email(None) is None


class TestExtractPhone:
    """Tests for extract_phone function."""

    def test_extracts_phone_with_dashes(self):
        text = "Call us at 555-123-4567"
        result = extract_phone(text)
        assert result is not None
        assert "555" in result

    def test_extracts_phone_with_parentheses(self):
        text = "Phone: (555) 123-4567"
        result = extract_phone(text)
        assert result is not None

    def test_handles_no_phone(self):
        assert extract_phone("No phone here") is None


class TestGenerateExternalId:
    """Tests for generate_external_id function."""

    def test_generates_id(self):
        result = generate_external_id("source", "123", "abc")
        assert result == "source_123_abc"

    def test_handles_single_identifier(self):
        result = generate_external_id("source", "123")
        assert result == "source_123"

    def test_skips_none_values(self):
        result = generate_external_id("source", "123", None, "456")
        assert result == "source_123_456"
