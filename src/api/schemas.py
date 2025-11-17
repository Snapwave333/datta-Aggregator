"""Pydantic schemas for API validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    api_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Contract schemas
class ContractBase(BaseModel):
    title: str
    description: Optional[str] = None
    agency: Optional[str] = None
    url: str


class ContractResponse(ContractBase):
    id: int
    external_id: str
    source_id: int
    department: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    estimated_value: Optional[float] = None
    posted_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[str] = None
    category: Optional[str] = None
    naics_code: Optional[str] = None
    set_aside: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractSearchQuery(BaseModel):
    keyword: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    status: Optional[str] = None
    naics_code: Optional[str] = None
    agency: Optional[str] = None
    page: int = 1
    page_size: int = 50


class ContractListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    contracts: List[ContractResponse]


# Source schemas
class SourceCreate(BaseModel):
    name: str
    base_url: str
    scraper_class: str
    description: Optional[str] = None
    source_type: str = "government"
    state: Optional[str] = None
    city: Optional[str] = None
    scrape_frequency_minutes: int = 60
    requires_javascript: bool = False
    rate_limit_seconds: int = 2


class SourceResponse(SourceCreate):
    id: int
    status: str
    last_scrape_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    total_contracts_found: int
    total_scrapes: int
    success_rate: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    total: int
    sources: List[SourceResponse]


# Statistics schemas
class StatisticsResponse(BaseModel):
    total_contracts: int
    open_contracts: int
    closed_contracts: int
    by_state: dict
    by_source: dict
    last_updated: str


# Scrape result schemas
class ScrapeResultResponse(BaseModel):
    source_id: int
    source_name: str
    success: bool
    contracts_found: int
    stats: dict
    error: Optional[str] = None
