"""Contract model for storing government contract/RFP data."""
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from src.models.database import Base


class ContractStatus(enum.Enum):
    """Status of a contract/RFP."""

    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class Contract(Base):
    """Model for government contracts and RFPs."""

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    # Core identifiers
    external_id = Column(String(255), nullable=False)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    url = Column(String(2048), nullable=False)

    # Contract details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    agency = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)

    # Financial information
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    estimated_value = Column(Float, nullable=True)

    # Dates
    posted_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    close_date = Column(DateTime, nullable=True)

    # Classification
    status = Column(Enum(ContractStatus), default=ContractStatus.UNKNOWN)
    category = Column(String(255), nullable=True)
    naics_code = Column(String(20), nullable=True)
    set_aside = Column(String(255), nullable=True)

    # Location
    state = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)

    # Contact information
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)

    # Metadata
    raw_data = Column(Text, nullable=True)  # JSON string of original scraped data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source = relationship("DataSource", back_populates="contracts")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_contract_due_date", "due_date"),
        Index("idx_contract_status", "status"),
        Index("idx_contract_state", "state"),
        Index("idx_contract_category", "category"),
        Index("idx_contract_source_external", "source_id", "external_id", unique=True),
    )

    def to_dict(self):
        """Convert contract to dictionary."""
        return {
            "id": self.id,
            "external_id": self.external_id,
            "source_id": self.source_id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "agency": self.agency,
            "department": self.department,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "estimated_value": self.estimated_value,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "close_date": self.close_date.isoformat() if self.close_date else None,
            "status": self.status.value if self.status else None,
            "category": self.category,
            "naics_code": self.naics_code,
            "set_aside": self.set_aside,
            "state": self.state,
            "city": self.city,
            "zip_code": self.zip_code,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
