"""User and subscription models for paid access."""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import Base


class SubscriptionTier(enum.Enum):
    """Subscription tiers."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Subscription(Base):
    """Model for user subscriptions."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    is_active = Column(Boolean, default=True)

    # Limits
    api_calls_per_day = Column(Integer, default=100)
    max_results_per_query = Column(Integer, default=50)

    # Billing
    price_per_month = Column(Integer, default=0)  # In cents
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_payment_at = Column(DateTime, nullable=True)

    # Usage tracking
    api_calls_today = Column(Integer, default=0)
    last_api_call_at = Column(DateTime, nullable=True)
    total_api_calls = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")


class User(Base):
    """Model for user accounts."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Profile
    company_name = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)

    # API access
    api_key = Column(String(255), unique=True, index=True, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    subscription = relationship(
        "Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "company_name": self.company_name,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
