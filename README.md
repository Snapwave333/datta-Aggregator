# GovContracts Pro - DaaS Contract Aggregator

A Data-as-a-Service (DaaS) platform that aggregates government contracts and RFPs from multiple sources into a single, searchable database.

## Overview

GovContracts Pro automates the collection of public government contract opportunities from various federal, state, and local procurement portals. It provides:

- **Automated Scraping**: 24/7 data collection from 50+ government websites
- **Data Aggregation**: Centralized database with deduplication and normalization
- **REST API**: Programmatic access to contract data
- **Web Portal**: User-friendly search interface
- **Subscription Management**: Tiered access with rate limiting

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Scrapers      │────▶│   Database   │◀────│   REST API  │
│ (Playwright/    │     │  (SQLite/    │     │  (FastAPI)  │
│  Requests)      │     │  PostgreSQL) │     │             │
└─────────────────┘     └──────────────┘     └─────────────┘
        │                       │                    │
        ▼                       ▼                    ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Scheduler     │     │  Aggregator  │     │ Web Portal  │
│  (APScheduler)  │     │              │     │  (HTML/JS)  │
└─────────────────┘     └──────────────┘     └─────────────┘
```

## Features

### Scraping Engine
- **Rate Limiting**: Configurable delays to respect website policies
- **Retry Logic**: Exponential backoff for failed requests
- **JavaScript Support**: Playwright for dynamic content
- **Random User Agents**: Avoid detection and blocking
- **Error Handling**: Robust error recovery and logging

### Data Sources
Pre-configured scrapers for:
- **Federal**: SAM.gov (System for Award Management)
- **California**: Cal eProcure
- **Texas**: SmartBuy/ESBD
- **New York**: Contract Reporter

Easily extensible to add more sources.

### API Features
- JWT and API Key authentication
- Full-text search across contracts
- Advanced filtering (state, category, value, dates)
- Pagination and rate limiting
- OpenAPI/Swagger documentation
- Admin endpoints for source management

### Web Portal
- Modern, responsive design
- Real-time search with filters
- Dashboard with statistics
- User registration and authentication
- Contract detail views with all metadata

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js (optional, for frontend development)
- SQLite (included) or PostgreSQL (production)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/datta-Aggregator.git
cd datta-Aggregator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install chromium
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Initialize database and sources**
```bash
python setup_sources.py
```

### Running the Application

**Start the API Server:**
```bash
python run_api.py
```
API will be available at: http://localhost:8000

**Start the Scraper Scheduler:**
```bash
python run_scraper.py
```
Scraper will run every 60 minutes (configurable).

**Access the Web Portal:**
Visit http://localhost:8000/portal

**API Documentation:**
Visit http://localhost:8000/docs (Swagger UI)

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./data/contracts.db

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Scraping
SCRAPE_INTERVAL_MINUTES=60
MAX_CONCURRENT_SCRAPERS=5
REQUEST_TIMEOUT_SECONDS=30
RATE_LIMIT_DELAY_SECONDS=2

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/daas.log
```

## API Usage

### Authentication

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe",
    "company_name": "Acme Corp"
  }'
```

**Get access token:**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### Search Contracts

**Basic search:**
```bash
curl -X GET "http://localhost:8000/contracts?keyword=construction" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Advanced search:**
```bash
curl -X GET "http://localhost:8000/contracts?\
keyword=technology&\
state=California&\
min_value=100000&\
status=open&\
due_after=2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Using API Key:**
```bash
curl -X GET "http://localhost:8000/contracts" \
  -H "X-API-Key: daas_your_api_key_here"
```

### Get Statistics

```bash
curl -X GET "http://localhost:8000/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Adding New Scrapers

1. **Create a new scraper class** in `src/scrapers/`:

```python
from src.scrapers.base import BaseScraper

class NewStateScraper(BaseScraper):
    def __init__(self, source_id: int):
        super().__init__(
            source_id=source_id,
            source_name="NewState_Procurement",
            base_url="https://procurement.newstate.gov",
        )

    async def get_listing_urls(self) -> List[str]:
        # Return URLs of pages to scrape
        return ["https://procurement.newstate.gov/search?page=1"]

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        # Parse HTML and return contract data
        contracts = []
        soup = self.parse_html(html)
        # ... extraction logic
        return contracts
```

2. **Register the scraper** in `src/scrapers/__init__.py`:

```python
from src.scrapers.new_state import NewStateScraper

SCRAPER_REGISTRY = {
    # ... existing scrapers
    "NewStateScraper": NewStateScraper,
}
```

3. **Add the data source** via API or setup script:

```python
manager.add_source(
    name="NewState Procurement",
    base_url="https://procurement.newstate.gov",
    scraper_class="NewStateScraper",
    state="NewState",
    scrape_frequency_minutes=120,
)
```

## Business Model

### Subscription Tiers

| Tier | Price/Month | API Calls/Day | Max Results |
|------|-------------|---------------|-------------|
| Free | $0 | 100 | 50 |
| Basic | $49 | 1,000 | 500 |
| Professional | $99 | 10,000 | 2,000 |
| Enterprise | $299 | Unlimited | Unlimited |

### Revenue Streams

1. **Subscription Fees**: Recurring monthly revenue from data access
2. **Custom Integrations**: One-time fees for API integration support
3. **Premium Sources**: Additional fee for specialized data sources
4. **Alerts & Notifications**: Premium feature for contract alerts

## Production Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["python", "run_api.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/contracts
    depends_on:
      - db

  scraper:
    build: .
    command: python run_scraper.py
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=securepass

volumes:
  pgdata:
```

### Security Recommendations

1. **Change default credentials** immediately after setup
2. **Use HTTPS** in production (nginx/traefik reverse proxy)
3. **Rotate API keys** regularly
4. **Monitor scraping** to respect robots.txt and rate limits
5. **Backup database** regularly
6. **Implement IP whitelisting** for admin endpoints

## Legal Considerations

- Ensure compliance with website Terms of Service
- Respect robots.txt directives
- Implement rate limiting to avoid service disruption
- Only scrape publicly available data
- Consider data retention policies
- Consult legal counsel for commercial use

## Project Structure

```
datta-Aggregator/
├── src/
│   ├── api/              # FastAPI REST API
│   │   ├── auth.py       # Authentication
│   │   ├── main.py       # API endpoints
│   │   └── schemas.py    # Pydantic models
│   ├── models/           # Database models
│   │   ├── contract.py   # Contract model
│   │   ├── source.py     # Data source model
│   │   └── user.py       # User & subscription
│   ├── processors/       # Data processing
│   │   ├── aggregator.py # Deduplication
│   │   └── scrape_manager.py
│   ├── scrapers/         # Web scrapers
│   │   ├── base.py       # Base scraper classes
│   │   ├── sam_gov.py    # Federal contracts
│   │   └── state_portals.py
│   ├── utils/            # Utilities
│   │   ├── helpers.py    # Data parsing
│   │   └── logger.py     # Logging setup
│   ├── config.py         # Configuration
│   └── scheduler.py      # Job scheduler
├── frontend/             # Web portal
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/                 # Database & logs
├── tests/                # Test suite
├── run_api.py            # Start API server
├── run_scraper.py        # Start scheduler
├── setup_sources.py      # Initialize data
└── requirements.txt      # Dependencies
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and feature requests, please open a GitHub issue.

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

**GovContracts Pro** - Aggregating opportunity, one contract at a time.
