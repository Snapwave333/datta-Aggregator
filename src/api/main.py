"""Main FastAPI application for DaaS Contract Aggregator."""
from datetime import timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.config import settings
from src.models import get_db, Contract, ContractStatus, DataSource, User, init_db
from src.api import schemas
from src.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    create_user,
    check_rate_limit,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.processors.aggregator import ContractAggregator
from src.processors.scrape_manager import ScrapeManager

# Create FastAPI app
app = FastAPI(
    title="DaaS Contract Aggregator API",
    description="API for searching aggregated government contracts and RFPs",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception:
    pass  # Frontend directory might not exist yet


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    from src.models.database import init_db
    init_db()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "DaaS Contract Aggregator API",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Aggregated government contracts and RFPs",
    }


# Serve frontend
@app.get("/portal")
async def portal():
    """Serve the web portal."""
    return FileResponse("frontend/index.html")


# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Get access token using username/password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=schemas.UserResponse)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
    )
    return user


@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


# Contract endpoints
@app.get("/contracts", response_model=schemas.ContractListResponse)
async def search_contracts(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    state: Optional[str] = Query(None, description="Filter by state"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_value: Optional[float] = Query(None, description="Minimum contract value"),
    max_value: Optional[float] = Query(None, description="Maximum contract value"),
    due_after: Optional[str] = Query(None, description="Due date after (ISO format)"),
    due_before: Optional[str] = Query(None, description="Due date before (ISO format)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Contract status"),
    naics_code: Optional[str] = Query(None, description="NAICS code"),
    agency: Optional[str] = Query(None, description="Agency name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search and filter contracts."""
    # Check rate limit
    if not check_rate_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily API rate limit exceeded",
        )

    # Build query
    query = db.query(Contract)

    # Apply filters
    if keyword:
        query = query.filter(
            or_(
                Contract.title.ilike(f"%{keyword}%"),
                Contract.description.ilike(f"%{keyword}%"),
                Contract.agency.ilike(f"%{keyword}%"),
            )
        )

    if state:
        query = query.filter(Contract.state == state)

    if category:
        query = query.filter(Contract.category.ilike(f"%{category}%"))

    if min_value is not None:
        query = query.filter(
            or_(
                Contract.estimated_value >= min_value,
                Contract.budget_min >= min_value,
            )
        )

    if max_value is not None:
        query = query.filter(
            or_(
                Contract.estimated_value <= max_value,
                Contract.budget_max <= max_value,
            )
        )

    if due_after:
        from datetime import datetime
        due_after_dt = datetime.fromisoformat(due_after.replace("Z", "+00:00"))
        query = query.filter(Contract.due_date >= due_after_dt)

    if due_before:
        from datetime import datetime
        due_before_dt = datetime.fromisoformat(due_before.replace("Z", "+00:00"))
        query = query.filter(Contract.due_date <= due_before_dt)

    if status_filter:
        try:
            status_enum = ContractStatus(status_filter)
            query = query.filter(Contract.status == status_enum)
        except ValueError:
            pass

    if naics_code:
        query = query.filter(Contract.naics_code.ilike(f"%{naics_code}%"))

    if agency:
        query = query.filter(Contract.agency.ilike(f"%{agency}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    contracts = query.order_by(Contract.due_date.asc()).offset(offset).limit(page_size).all()

    # Respect subscription limits
    if current_user.subscription:
        max_results = current_user.subscription.max_results_per_query
        contracts = contracts[:max_results]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "contracts": contracts,
    }


@app.get("/contracts/{contract_id}", response_model=schemas.ContractResponse)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific contract by ID."""
    if not check_rate_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily API rate limit exceeded",
        )

    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    return contract


@app.get("/contracts/states", response_model=List[str])
async def get_states(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of all states with contracts."""
    states = db.query(Contract.state).distinct().all()
    return [s[0] for s in states if s[0]]


@app.get("/statistics", response_model=schemas.StatisticsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get aggregation statistics."""
    if not check_rate_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily API rate limit exceeded",
        )

    aggregator = ContractAggregator(db)
    return aggregator.get_statistics()


# Admin endpoints
@app.get("/admin/sources", response_model=schemas.SourceListResponse)
async def list_sources(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all data sources (admin only)."""
    sources = db.query(DataSource).all()
    return {"total": len(sources), "sources": sources}


@app.post("/admin/sources", response_model=schemas.SourceResponse)
async def create_source(
    source_data: schemas.SourceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new data source (admin only)."""
    manager = ScrapeManager(db)
    source = manager.add_source(**source_data.dict())
    return source


@app.post("/admin/scrape/{source_id}", response_model=schemas.ScrapeResultResponse)
async def trigger_scrape(
    source_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Trigger scraping for a specific source (admin only)."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    manager = ScrapeManager(db)
    import asyncio
    result = asyncio.run(manager.scrape_source(source))
    return result


@app.post("/admin/scrape-all", response_model=List[schemas.ScrapeResultResponse])
async def trigger_scrape_all(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Trigger scraping for all active sources (admin only)."""
    manager = ScrapeManager(db)
    import asyncio
    results = asyncio.run(manager.scrape_all_sources())
    return results


# Import datetime at module level
from datetime import datetime
