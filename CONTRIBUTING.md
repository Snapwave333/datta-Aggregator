# Contributing to GovContracts Pro

First off, thank you for considering contributing to GovContracts Pro! It's people like you that make this platform a great tool for the government contracting community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Adding New Scrapers](#adding-new-scrapers)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming, inclusive environment. Please be respectful, professional, and constructive in all interactions.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Great Bug Reports Include:**
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots if applicable
- Your environment details (OS, Python version, etc.)

### 💡 Suggesting Enhancements

We love new ideas! Enhancement suggestions are tracked as GitHub issues.

**Great Enhancement Suggestions Include:**
- A clear, descriptive title
- Detailed explanation of the proposed functionality
- Why this enhancement would be useful
- Possible implementation approaches

### 🕷️ Adding New Scrapers

One of the most valuable contributions is adding scrapers for new government data sources!

**Steps to add a new scraper:**

1. Research the target website's structure
2. Check robots.txt and Terms of Service
3. Create scraper class in `src/scrapers/`
4. Register in `SCRAPER_REGISTRY`
5. Add comprehensive tests
6. Document the data source

**Example Scraper Template:**

```python
from src.scrapers.base import BaseScraper
from typing import List, Dict, Any

class NewSourceScraper(BaseScraper):
    """Scraper for [Source Name] - [Description]."""

    def __init__(self, source_id: int):
        super().__init__(
            source_id=source_id,
            source_name="Source_Name",
            base_url="https://example.gov",
        )

    async def get_listing_urls(self) -> List[str]:
        """Return URLs of pages containing listings."""
        # Implement pagination logic
        pass

    async def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """Extract contract data from HTML."""
        # Implement parsing logic
        pass
```

### 🔄 Pull Requests

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes thoroughly
6. **Commit** with clear messages
7. **Push** to your fork
8. **Open** a Pull Request

**PR Checklist:**
- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] All existing tests pass
- [ ] Documentation updated if needed
- [ ] No sensitive data (API keys, credentials) included

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/datta-Aggregator.git
cd datta-Aggregator

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Install Playwright
playwright install chromium

# Setup environment
cp .env.example .env
```

## 📝 Style Guidelines

### Python Code

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Write **docstrings** for all public methods
- Maximum line length: **100 characters**
- Use **black** for formatting: `black src/ tests/`

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Keep README updated with new features
- Add docstrings for all public APIs

### Testing

- Write tests for all new functionality
- Maintain >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run linting
flake8 src/ tests/
black --check src/ tests/
```

## 💬 Commit Messages

Use clear, descriptive commit messages:

**Format:**
```
<type>: <short summary>

<optional body>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add Florida VBS scraper

- Implements scraper for Florida Vendor Bid System
- Includes rate limiting and pagination
- Adds unit tests for parsing logic
```

```
fix: resolve authentication token expiration issue

Tokens were not being refreshed properly, causing
users to be logged out unexpectedly.

Fixes #123
```

## 🎯 Priority Areas

We especially welcome contributions in:

- **New Scrapers**: Add support for more state/local government sources
- **Frontend Improvements**: Enhance the web portal UI/UX
- **Performance**: Optimize scraping and database queries
- **Testing**: Increase test coverage and add integration tests
- **Documentation**: Improve docs and add tutorials
- **Accessibility**: Make the platform more accessible

## 🙋 Questions?

Feel free to open an issue for any questions about contributing. We're here to help!

---

Thank you for contributing to GovContracts Pro! Your efforts help the government contracting community access opportunities more efficiently.
