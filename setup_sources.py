#!/usr/bin/env python3
"""Set up initial data sources for the DaaS Contract Aggregator."""
from src.models.database import init_db, SessionLocal
from src.processors.scrape_manager import ScrapeManager
from src.api.auth import create_user
from src.utils.logger import get_logger

logger = get_logger("setup")


def setup_default_sources():
    """Add default government contract sources."""
    db = SessionLocal()
    manager = ScrapeManager(db)

    # Define default sources
    default_sources = [
        {
            "name": "SAM.gov Federal Contracts",
            "base_url": "https://sam.gov",
            "scraper_class": "SAMGovScraper",
            "description": "Federal government contract opportunities from SAM.gov",
            "source_type": "federal",
            "state": None,
            "city": None,
            "scrape_frequency_minutes": 60,
            "requires_javascript": True,
            "rate_limit_seconds": 3,
        },
        {
            "name": "California eProcure",
            "base_url": "https://caleprocure.ca.gov",
            "scraper_class": "CaliforniaScraper",
            "description": "California state government procurement opportunities",
            "source_type": "state",
            "state": "California",
            "city": "Sacramento",
            "scrape_frequency_minutes": 120,
            "requires_javascript": True,
            "rate_limit_seconds": 2,
        },
        {
            "name": "Texas SmartBuy",
            "base_url": "https://www.txsmartbuy.gov",
            "scraper_class": "TexasScraper",
            "description": "Texas Electronic State Business Daily",
            "source_type": "state",
            "state": "Texas",
            "city": "Austin",
            "scrape_frequency_minutes": 120,
            "requires_javascript": False,
            "rate_limit_seconds": 2,
        },
        {
            "name": "New York Contract Reporter",
            "base_url": "https://www.nyscr.ny.gov",
            "scraper_class": "NewYorkScraper",
            "description": "New York State Contract Reporter",
            "source_type": "state",
            "state": "New York",
            "city": "Albany",
            "scrape_frequency_minutes": 120,
            "requires_javascript": True,
            "rate_limit_seconds": 2,
        },
    ]

    # Add sources
    for source_config in default_sources:
        try:
            # Check if source already exists
            from src.models.source import DataSource

            existing = (
                db.query(DataSource)
                .filter(DataSource.name == source_config["name"])
                .first()
            )

            if existing:
                logger.info(f"Source already exists: {source_config['name']}")
                continue

            source = manager.add_source(**source_config)
            logger.info(f"Added source: {source.name} (ID: {source.id})")

        except Exception as e:
            logger.error(f"Failed to add source {source_config['name']}: {e}")

    db.close()


def setup_admin_user():
    """Create a default admin user."""
    db = SessionLocal()

    try:
        # Check if admin exists
        from src.models.user import User

        existing = db.query(User).filter(User.email == "admin@govcontracts.pro").first()

        if existing:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin = create_user(
            db=db,
            email="admin@govcontracts.pro",
            password="admin123",  # Change in production!
            full_name="System Administrator",
            company_name="GovContracts Pro",
            is_admin=True,
        )

        # Upgrade subscription
        admin.subscription.tier = "ENTERPRISE"
        admin.subscription.api_calls_per_day = 100000
        admin.subscription.max_results_per_query = 10000
        db.commit()

        logger.info(f"Created admin user: {admin.email}")
        logger.info(f"Admin API key: {admin.api_key}")
        logger.info("IMPORTANT: Change the default password immediately!")

    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized")

    print("\nSetting up default data sources...")
    setup_default_sources()

    print("\nCreating admin user...")
    setup_admin_user()

    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Update the admin password immediately")
    print("2. Configure your .env file with proper settings")
    print("3. Run the API server: python run_api.py")
    print("4. Run the scraper scheduler: python run_scraper.py")
    print("5. Visit http://localhost:8000/portal to access the web portal")
