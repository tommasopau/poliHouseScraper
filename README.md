# Rental Finder

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-org/rental-finder/actions)

<!-- Tech Stack Icons -->
<p>
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/" target="_blank"><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://sqlmodel.tiangolo.com/" target="_blank"><img src="https://img.shields.io/badge/SQLModel-3C3C3C?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLModel"></a>
  <a href="https://supabase.com/" target="_blank"><img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"></a>
  <a href="https://core.telegram.org/" target="_blank"><img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
</p>

## Description

**Rental Finder** is a Python/FastAPI/SQLModel application that scrapes rental listings from Telegram channels, parses and stores them in a Supabase PostgreSQL database, and exposes robust API endpoints for searching and filtering rental properties. The project enables users to efficiently discover rental opportunities with advanced filters and integrates LLM parsing for structured data extraction.

---

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Setup & Migrations](#database-setup--migrations)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```sh
# Clone the repository
git clone https://github.com/your-org/rental-finder.git
cd rental-finder

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root with the following environment variables (Distance Matrix API https://distancematrix.ai/product):

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL_SUPABASE=postgresql+asyncpg://user:password@host:port/dbname
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=your_telegram_phone_number
TELEGRAM_SESSION_NAME=house_scraper
TELEGRAM_SESSION_STRING=your_telegram_session_string
MISTRAL_API_KEY=your_mistral_api_key
DISTANCE_MATRIX_API_KEY=your_distance_matrix_api_key
```

> **Note:** See `app/core/config.py` for all supported settings.

---

## Usage

### Run the Development Server

```sh
uvicorn app.main:app --reload
```

### Example API Calls

#### Search Rentals with Filters

```sh
curl -X GET "http://localhost:8000/api/rentals/?limit=10&offset=0&property_type=appartamento&tenant_preference=ragazza"
```

#### Using httpx (Python)

```python
import httpx

response = httpx.get(
    "http://localhost:8000/api/rentals/",
    params={
        "limit": 5,
        "offset": 0,
        "property_type": "camera_singola",
        "tenant_preference": "indifferente"
    }
)
print(response.json())
```

---

## Database Setup & Migrations

### Alembic Migrations

```sh
# Initialize Alembic (if not already done)
alembic upgrade head
```

See migration scripts in `alembic/versions`.

### SQLModel Table Creation (Development)

Tables are auto-created on startup via:

```python
from app.db.manage_db import init_db
await init_db()
```

---

## Testing

Run tests with pytest:

```sh
# Ensure test database is configured in .env
pytest
```

- Tests are located in `tests`.
- Use fixtures for database isolation and mocking external APIs.

---

## Deployment

- **Railway/Supabase:** Supports free-tier deployment. Set environment variables in Railway/Supabase dashboard.
- **CI/CD:** Automated tests via GitHub Actions (`.github/workflows/python-app.yml`).
- **Production:** Use `Procfile` for deployment platforms supporting Gunicorn/Uvicorn.

---

## Contributing

- **Branching:** Use `main` for stable releases, feature branches for development.
- **Code Style:** Follow [PEP8](https://peps.python.org/pep-0008/) and use `black` for formatting.
- **Pull Requests:** Submit PRs with clear descriptions and link related issues. Ensure all tests pass.

---

## License

MIT License
