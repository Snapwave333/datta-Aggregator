"""Configuration management for DaaS Contract Aggregator."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./data/contracts.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 1440

    # Scraping
    scrape_interval_minutes: int = 60
    max_concurrent_scrapers: int = 5
    request_timeout_seconds: int = 30
    rate_limit_delay_seconds: float = 2.0

    # Logging
    log_level: str = "INFO"
    log_file: str = "./data/daas.log"

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure data directory exists
settings.data_dir.mkdir(exist_ok=True)
