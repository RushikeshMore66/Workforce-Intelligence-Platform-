# Workforce Intelligence Platform (WIP)

## Overview
The Workforce Intelligence Platform (WIP) is a comprehensive SaaS application designed to manage and monitor workforce productivity, project health, and task delivery. It provides granular role-based access control (RBAC) to ensure that users—ranging from Owners to Workers—only see and interact with data relevant to their role and assignments.

## Architecture

### Frontend
- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS
- **Authentication:** JWT-based authentication stored in `localStorage`
- **Data Fetching:** Custom `apiClient` wrapping standard `fetch` API, communicating directly with the backend.
- **Key Features:**
  - Real-time dashboard with dynamic metrics
  - Intelligence page highlighting critical risks and blockers
  - Project and task management views
  - Workforce directory with team-based filtering

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy with Alembic for migrations
- **Authentication:** OAuth2 with Password Flow (Bearer JWT)
- **RBAC:** Strict policy-enforced endpoint access (Owner, Supervisor, Team Leader, Worker)
- **Key Modules:**
  - `auth`: Handles login and user profile retrieval
  - `projects`, `tasks`, `teams`, `workers`: Core entities management
  - `dashboard`, `analytics`: Complex data aggregation and business intelligence
  - `notifications`: Actionable alerts for the end-user

## Database Setup and Seeding
The application uses a PostgreSQL database named `workforce_intelligence`.

### Connecting to Database
Use the following credentials to connect to the database (configured in `backend/.env`):
- **User:** `postgres`
- **Password:** `9067717776`
- **Port:** `5432`

### Seeding Data
A comprehensive seeding script is provided to populate the database with realistic scenarios (projects, tasks, blockers, etc.) without relying on dummy runtime data.
To seed the database, run:
```bash
cd backend
python seed.py
```

### Demo Accounts
The following demo accounts are available after seeding (Password for all: `WipDev2024!`):
- `owner@wip.dev` → OWNER
- `supervisor1@wip.dev` → SUPERVISOR (Backend team)
- `supervisor2@wip.dev` → SUPERVISOR (Frontend team)
- `leader1@wip.dev` → TEAM_LEADER (Backend)
- `leader2@wip.dev` → TEAM_LEADER (Frontend)
- `worker1@wip.dev` → WORKER (Backend)

## Running the Application Locally

### 1. Start the Backend (FastAPI)
```bash
cd backend
# Ensure virtual environment is activated
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Frontend (Next.js)
```bash
# In the project root
npm run dev
```
The application will be accessible at `http://localhost:3000`.

## Final Audit & Completion Status
The application has undergone a full system audit:
- ✅ **Database Migration:** Successfully migrated from SQLite to PostgreSQL.
- ✅ **Real Data Integration:** Removed all frontend mock data (`USE_MOCK=false`). All API modules (`projects.ts`, `dashboard.ts`, `workers.ts`, `notifications.ts`, `activities.ts`, `auth.ts`, `supervisors.ts`, `teams.ts`, `blockers.ts`, `reports.ts`, `analytics.ts`) now communicate directly with the live FastAPI backend.
- ✅ **UI Fixes:** Corrected the Intelligence page to show real computed attention items instead of static cards. Fixed Workforce page to show resolved team names instead of raw IDs. Cleaned up Settings page demo artifacts.
- ✅ **Backend Logic Fixes:** Implemented real SQL queries for the Dashboard service. Corrected Task count aggregation in Teams and Workers endpoints. Added missing `/notifications/unread-count` endpoint.
- ✅ **RBAC Verification:** Validated that Supervisors and Workers can only access their scoped data.
- ✅ **Clean Repository:** Removed unused mock scripts and consolidated info into this document.

The product is now coherent, polished, locally runnable, and genuinely usable.
