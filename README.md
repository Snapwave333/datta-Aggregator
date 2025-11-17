<div align="center">

# 🏛️ GovContracts Pro

### **Data-as-a-Service Platform for Government Contract Intelligence**

*Transform scattered government procurement data into actionable business opportunities*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

[**Explore Docs »**](#-documentation) · [**View Demo**](#-quick-start) · [**Report Bug**](../../issues) · [**Request Feature**](../../issues)

---

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" alt="rainbow line" width="100%">

</div>

## 🎯 The Problem We Solve

<table>
<tr>
<td width="50%">

### ❌ Without GovContracts Pro

- 🕐 **100+ hours/month** manually searching
- 📊 Fragmented data across 50+ websites
- 🚫 Missing critical opportunities
- 💸 Paying for multiple subscriptions
- 📉 Inconsistent data formats

</td>
<td width="50%">

### ✅ With GovContracts Pro

- ⚡ **< 5 minutes** to find opportunities
- 🎯 Single source of truth
- 🔔 Never miss a contract again
- 💰 One subscription, all data
- 📈 Clean, normalized database

</td>
</tr>
</table>

---

## ✨ Key Features

<div align="center">

| 🤖 **Automated Scraping** | 🔄 **Smart Aggregation** | 🔒 **Enterprise Security** |
|:---:|:---:|:---:|
| 24/7 data collection from 50+ government sources with intelligent rate limiting | Deduplication, normalization, and enrichment of contract data | JWT + API Key auth with role-based access control |

| 🔍 **Powerful Search** | 📊 **Analytics Dashboard** | 🚀 **Developer API** |
|:---:|:---:|:---:|
| Full-text search with advanced filters (state, value, category, dates) | Real-time statistics and visual insights | RESTful API with Swagger docs |

</div>

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Data Collection Layer"
        S1[SAM.gov Scraper]
        S2[California eProcure]
        S3[Texas SmartBuy]
        S4[New York Reporter]
        S5[+ 46 More Sources]
    end

    subgraph "Processing Layer"
        SC[Scheduler<br/>APScheduler]
        AG[Aggregator<br/>Deduplication]
        DB[(Database<br/>PostgreSQL)]
    end

    subgraph "Service Layer"
        API[REST API<br/>FastAPI]
        AUTH[Auth Service<br/>JWT + API Keys]
    end

    subgraph "Client Layer"
        WEB[Web Portal]
        SDK[API Clients]
        HOOK[Webhooks]
    end

    S1 & S2 & S3 & S4 & S5 --> SC
    SC --> AG
    AG --> DB
    DB --> API
    AUTH --> API
    API --> WEB & SDK & HOOK

    style DB fill:#f9f,stroke:#333,stroke-width:2px
    style API fill:#bbf,stroke:#333,stroke-width:2px
```

---

## 🚀 Quick Start

### Prerequisites

- 🐍 Python 3.9 or higher
- 📦 pip (Python package manager)
- 🗄️ SQLite (included) or PostgreSQL (production)

### ⚡ One-Click Setup

```bash
# Clone the repository
git clone https://github.com/Snapwave333/datta-Aggregator.git
cd datta-Aggregator

# Run automated setup
chmod +x setup.sh && ./setup.sh
```

### 📝 Manual Installation

<details>
<summary><b>Click to expand step-by-step guide</b></summary>

**1️⃣ Clone & Setup Environment**
```bash
git clone https://github.com/Snapwave333/datta-Aggregator.git
cd datta-Aggregator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

**3️⃣ Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

**4️⃣ Initialize Database**
```bash
python setup_sources.py
```

**5️⃣ Start Services**
```bash
# Terminal 1: Start API Server
python run_api.py

# Terminal 2: Start Scraper Scheduler
python run_scraper.py
```

**6️⃣ Access Application**
- 🌐 Web Portal: http://localhost:8000/portal
- 📚 API Docs: http://localhost:8000/docs
- 🔧 Admin Panel: http://localhost:8000/admin

</details>

---

## 💻 Usage

### 🔐 Authentication

<table>
<tr>
<td>

**Register New User**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "SecurePass123!",
    "company_name": "Construction Co"
  }'
```

</td>
<td>

**Get Access Token**
```bash
curl -X POST "http://localhost:8000/token" \
  -d "username=user@company.com" \
  -d "password=SecurePass123!"
```

</td>
</tr>
</table>

### 🔍 Search Contracts

```bash
# Basic keyword search
curl -X GET "http://localhost:8000/contracts?keyword=construction" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Advanced multi-filter search
curl -X GET "http://localhost:8000/contracts?\
keyword=infrastructure&\
state=California&\
min_value=500000&\
max_value=5000000&\
status=open&\
due_after=2024-06-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 📊 Get Statistics

```bash
curl -X GET "http://localhost:8000/statistics" \
  -H "X-API-Key: YOUR_API_KEY"
```

<details>
<summary><b>📋 Example Response</b></summary>

```json
{
  "total_contracts": 15847,
  "open_contracts": 3241,
  "closed_contracts": 12606,
  "by_state": {
    "Federal": 5234,
    "California": 3421,
    "Texas": 2891,
    "New York": 2156,
    "Florida": 1145
  },
  "by_source": {
    "SAM.gov": 5234,
    "Cal eProcure": 3421,
    "Texas SmartBuy": 2891,
    "NY Contract Reporter": 2156
  },
  "last_updated": "2024-11-17T15:30:00Z"
}
```

</details>

---

## 🎨 Web Portal Features

<div align="center">

### 📊 **Interactive Dashboard**
*Real-time statistics with beautiful visualizations*

### 🔍 **Advanced Search Interface**
*Multi-criteria filtering with instant results*

### 📱 **Responsive Design**
*Perfect experience on desktop, tablet, and mobile*

### 🔔 **Smart Notifications**
*Get alerts for contracts matching your criteria*

</div>

---

## 💰 Business Model & Pricing

<div align="center">

| Plan | Monthly Price | API Calls/Day | Results/Query | Features |
|:---:|:---:|:---:|:---:|:---|
| **🆓 Free** | $0 | 100 | 50 | Basic search, Limited history |
| **🥉 Basic** | $49 | 1,000 | 500 | Email alerts, Export CSV |
| **🥈 Professional** | $99 | 10,000 | 2,000 | Webhooks, Priority support |
| **🥇 Enterprise** | $299 | Unlimited | Unlimited | Custom scrapers, SLA, Dedicated support |

</div>

### 💵 Revenue Streams

- 🔄 **Recurring Subscriptions** - Monthly/Annual plans
- 🔧 **Custom Integrations** - API integration services
- 📊 **Premium Data Sources** - Specialized industry data
- 🚨 **Alert Services** - Real-time contract notifications
- 📈 **Analytics Add-ons** - Advanced reporting tools

---

## 🔧 Configuration

### Environment Variables

```env
# 🗄️ Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/contracts

# 🌐 API Settings
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-256-bit-secret-key-here

# 🤖 Scraping Configuration
SCRAPE_INTERVAL_MINUTES=60
MAX_CONCURRENT_SCRAPERS=5
REQUEST_TIMEOUT_SECONDS=30
RATE_LIMIT_DELAY_SECONDS=2

# 📝 Logging
LOG_LEVEL=INFO
LOG_FILE=./data/daas.log
```

---

## 🔌 Adding New Data Sources

<details>
<summary><b>📖 Step-by-Step Guide</b></summary>

### 1️⃣ Create Scraper Class

```python
# src/scrapers/florida_scraper.py
from src.scrapers.base import BaseScraper
from typing import List, Dict, Any

class FloridaScraper(BaseScraper):
    """Scraper for Florida VBS (Vendor Bid System)."""

    def __init__(self, source_id: int):
        super().__init__(
            source_id=source_id,
            source_name="Florida_VBS",
            base_url="https://vendor.myfloridamarketplace.com",
        )

    async def get_listing_urls(self) -> List[str]:
        """Return URLs to scrape."""
        return [
            f"{self.base_url}/search?page={i}"
            for i in range(1, 11)
        ]

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Extract contract data from HTML."""
        contracts = []
        soup = self.parse_html(html)

        for item in soup.find_all("div", class_="bid-item"):
            contracts.append({
                "external_id": self._extract_id(item),
                "title": self._extract_title(item),
                "due_date": self._extract_date(item),
                # ... more fields
            })

        return contracts
```

### 2️⃣ Register Scraper

```python
# src/scrapers/__init__.py
from src.scrapers.florida_scraper import FloridaScraper

SCRAPER_REGISTRY = {
    # ... existing scrapers
    "FloridaScraper": FloridaScraper,
}
```

### 3️⃣ Add Data Source

```python
# Via API or setup script
manager.add_source(
    name="Florida VBS",
    base_url="https://vendor.myfloridamarketplace.com",
    scraper_class="FloridaScraper",
    state="Florida",
    scrape_frequency_minutes=120,
)
```

</details>

---

## 🐳 Docker Deployment

<details>
<summary><b>🚀 Production-Ready Docker Setup</b></summary>

**Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps

COPY . .

EXPOSE 8000

CMD ["python", "run_api.py"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://daas:securepass@db/contracts
    depends_on:
      - db
    restart: unless-stopped

  scraper:
    build: .
    command: python run_scraper.py
    environment:
      - DATABASE_URL=postgresql://daas:securepass@db/contracts
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=daas
      - POSTGRES_PASSWORD=securepass
      - POSTGRES_DB=contracts
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  pgdata:
```

**Deploy**
```bash
docker-compose up -d
```

</details>

---

## 📁 Project Structure

```
datta-Aggregator/
├── 📂 src/                          # Source code
│   ├── 📂 api/                      # REST API (FastAPI)
│   │   ├── auth.py                  # Authentication & authorization
│   │   ├── main.py                  # API endpoints
│   │   └── schemas.py               # Pydantic models
│   ├── 📂 models/                   # Database models (SQLAlchemy)
│   │   ├── contract.py              # Contract entity
│   │   ├── source.py                # Data source entity
│   │   └── user.py                  # User & subscriptions
│   ├── 📂 processors/               # Data processing logic
│   │   ├── aggregator.py            # Deduplication & normalization
│   │   └── scrape_manager.py        # Orchestrates scraping jobs
│   ├── 📂 scrapers/                 # Web scraping modules
│   │   ├── base.py                  # Base scraper classes
│   │   ├── sam_gov.py               # Federal contracts (SAM.gov)
│   │   └── state_portals.py         # State government scrapers
│   ├── 📂 utils/                    # Utility functions
│   │   ├── helpers.py               # Data parsing helpers
│   │   └── logger.py                # Logging configuration
│   ├── config.py                    # Application configuration
│   └── scheduler.py                 # Job scheduling (APScheduler)
├── 📂 frontend/                     # Web portal frontend
│   ├── index.html                   # Main HTML template
│   ├── styles.css                   # Styling
│   └── app.js                       # Frontend JavaScript
├── 📂 tests/                        # Test suite
│   └── test_helpers.py              # Unit tests
├── 📂 data/                         # Database & logs (gitignored)
├── 📄 run_api.py                    # Start API server
├── 📄 run_scraper.py                # Start scraper daemon
├── 📄 setup_sources.py              # Initialize database
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment template
└── 📄 README.md                     # You are here! 👋
```

---

## 🔒 Security Best Practices

<div align="center">

| Security Feature | Implementation |
|:---|:---|
| 🔐 **Password Hashing** | bcrypt with salt |
| 🎟️ **Token Security** | JWT with expiration |
| 🚦 **Rate Limiting** | Per-user API quotas |
| 🛡️ **Input Validation** | Pydantic schemas |
| 🔑 **API Key Rotation** | Unique keys per user |
| 📝 **Audit Logging** | All actions tracked |

</div>

### ⚠️ Important Security Notes

1. **Change default credentials** immediately after installation
2. **Use HTTPS** in production (nginx/traefik reverse proxy)
3. **Rotate secrets** regularly (JWT secret, API keys)
4. **Monitor logs** for suspicious activity
5. **Backup database** with encryption
6. **Implement firewall** rules for admin endpoints

---

## ⚖️ Legal & Ethical Considerations

> **Important:** This tool is designed for ethical data collection of **publicly available** government information.

- ✅ Respect `robots.txt` directives
- ✅ Implement rate limiting to avoid service disruption
- ✅ Comply with Terms of Service
- ✅ Only scrape public data
- ✅ Maintain data retention policies
- ✅ Consult legal counsel before commercial deployment

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_helpers.py -v
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 **Fork** the repository
2. 🌿 **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💻 **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 **Push** to the branch (`git push origin feature/AmazingFeature`)
5. 🔃 **Open** a Pull Request

### 📋 Contribution Ideas

- 🌍 Add scrapers for more states/countries
- 🎨 Improve frontend UI/UX
- 📊 Add more analytics features
- 🔔 Implement email notifications
- 📱 Build mobile app
- 🧪 Increase test coverage

---

## 🗺️ Roadmap

- [x] Core scraping framework
- [x] REST API with authentication
- [x] Web portal with search
- [x] Subscription management
- [ ] 🔜 Email notification system
- [ ] 🔜 Machine learning contract matching
- [ ] 🔜 Mobile application
- [ ] 🔜 Advanced analytics dashboard
- [ ] 🔜 Slack/Teams integration
- [ ] 🔜 Automated bid response generation

---

## 📬 Support & Contact

<div align="center">

**Need Help?**

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-red?style=for-the-badge&logo=github)](../../issues)
[![Discussions](https://img.shields.io/badge/GitHub-Discussions-purple?style=for-the-badge&logo=github)](../../discussions)

</div>

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling
- All the amazing open source contributors

---

<div align="center">

### ⭐ Star This Repository!

If you find this project useful, please consider giving it a star. It helps others discover this tool!

[![GitHub stars](https://img.shields.io/github/stars/Snapwave333/datta-Aggregator?style=social)](../../stargazers)

---

**Built with ❤️ for the Government Contracting Community**

*"Transforming procurement chaos into business opportunity"*

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" alt="rainbow line" width="100%">

**[⬆ Back to Top](#-govcontracts-pro)**

</div>
