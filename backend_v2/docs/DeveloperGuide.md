# Developer & Setup Guide — Product Guardian Network (PGN)

This guide helps developers set up, run, test, and write code for the PGN backend.

---

## 1. Quick Start Local Setup

### Step 1: Install Dependencies
Ensure you have Python 3.12 installed. Run:
```powershell
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` and set:
```ini
DATABASE_URL=postgresql://expiry_user:expiry_pass@localhost:5432/expiry_db
APP_ENV=development
SECRET_KEY=change_this_secret_key
```

### Step 3: Run Database Migrations
Compile the PostgreSQL tables and schema configuration direct to database instance:
```powershell
python -c "from app.database import Base, engine; from app.models import *; Base.metadata.create_all(engine)"
```

### Step 4: Seed Database
Populate user profiles, reports, credibility metrics, clusters, safety alerts, and case logs:
```powershell
python scripts/seed_community.py
```

### Step 5: Start Local Server
Run the FastAPI development uvicorn server:
```powershell
python -m uvicorn app.main:app --port 8001 --reload
```
Swagger UI will be accessible at: `http://127.0.0.1:8001/docs`

---

## 2. Running Tests

### Integration E2E Test Suite
To verify all Phase 1-6 APIs, validation rules, alerts, and cases:
```powershell
python scripts/test_pgn_endpoints.py
```

### Pytest Unit/Integration Suite
Execute the pytest suite:
```powershell
pytest tests/
```
