#!/usr/bin/env python3
"""Run the DaaS Contract Aggregator API server."""
import uvicorn
from src.config import settings
from src.models.database import init_db
from src.api.main import app

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized")

    # Run the API server
    print(f"Starting API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
