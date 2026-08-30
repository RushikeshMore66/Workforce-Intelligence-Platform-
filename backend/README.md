# Workforce Intelligence — Backend API

Production-ready FastAPI backend for the **Workforce Intelligence** platform.

---

## 🏗️ Architecture Overview

The backend is built with a clean layered architecture adhering to SOLID and Domain-Driven Design principles:

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point, CORS & exception handlers
│   ├── config.py            # Pydantic Settings & environment configuration
│   ├── database.py          # SQLAlchemy 2.0 engine, declarative base & session generator
│   │
│   ├── models/              # SQLAlchemy ORM models (User, Project, Task, Blocker, Team, etc.)
│   ├── schemas/             # Pydantic models for request/response validation & serialization
│   ├── routers/             # FastAPI API routers (/auth, /projects, /workers, /dashboard, etc.)
│   ├── services/            # Business logic layer (project creation, analytics, metrics calculation)
│   ├── repositories/        # Data access layer (Repository pattern for clean DB abstraction)
│   ├── auth/                # JWT token generation, OAuth2 bearer & RBAC role dependencies
│   └── core/                # Security helpers, custom exceptions & response envelopes
│
├── migrations/              # Alembic database migration scripts
├── tests/                   # Pytest test suite with isolated SQLite database fixtures
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ (or SQLite for local development/testing)

### 2. Set Up Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy or customize `.env`:
```bash
# Example DATABASE_URL for PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workforce_intelligence

# Or use SQLite for rapid local testing
# DATABASE_URL=sqlite:///./workforce.db
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start the Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **API Base URL**: `http://localhost:8000/api/v1`
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Tests

Execute the automated test suite using `pytest`:

```bash
pytest -v
```

---

## 🔐 Default Authentication Credentials

For initial testing and demo access, the database seeds an Owner user:
- **Email**: `rajesh.mehta@apexsoftware.in`
- **Password**: `password123`
- **Role**: `OWNER`
