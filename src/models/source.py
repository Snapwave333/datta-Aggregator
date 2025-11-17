"""Data source model for tracking scraped websites."""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from src.models.database import Base


class SourceStatus(enum.Enum):
    """Status of a data source."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DataSource(Base):
    """Model for tracking data sources (websites to scrape)."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)

    # Source identification
    name = Column(String(255), nullable=False, unique=True)
    base_url = Column(String(2048), nullable=False)
    scraper_class = Column(String(255), nullable=False)

    # Source metadata
    description = Column(Text, nullable=True)
    source_type = Column(String(50), default="government")  # government, federal, state, city
    state = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)

    # Scraping configuration
    scrape_frequency_minutes = Column(Integer, default=60)
    requires_javascript = Column(Boolean, default=False)
    rate_limit_seconds = Column(Integer, default=2)

    # Status tracking
    status = Column(Enum(SourceStatus), default=SourceStatus.ACTIVE)
    last_scrape_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    total_contracts_found = Column(Integer, default=0)
    total_scrapes = Column(Integer, default=0)
    success_rate = Column(Integer, default=100)  # Percentage

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contracts = relationship("Contract", back_populates="source", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert source to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "base_url": self.base_url,
            "scraper_class": self.scraper_class,
            "description": self.description,
            "source_type": self.source_type,
            "state": self.state,
            "city": self.city,
            "scrape_frequency_minutes": self.scrape_frequency_minutes,
            "requires_javascript": self.requires_javascript,
            "rate_limit_seconds": self.rate_limit_seconds,
            "status": self.status.value if self.status else None,
            "last_scrape_at": self.last_scrape_at.isoformat() if self.last_scrape_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_error": self.last_error,
            "total_contracts_found": self.total_contracts_found,
            "total_scrapes": self.total_scrapes,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
