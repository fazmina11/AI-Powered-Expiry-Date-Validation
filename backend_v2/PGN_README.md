# Product Guardian Network (PGN) — Production-Ready Backend v1.0
## Community Product Reporting, Credibility, Clustering, Intelligence, Safety Alerts & Case Management

Welcome to PGN backend v1.0. This backend manages consumer product reports, credibility engines, issue clustering, safety alerts, structured log management, and case investigations.

---

## 📂 Project Structure

```
backend_v2/
├── alembic/
│   └── versions/          # Alembic migrations tracking
├── app/
│   ├── config.py          # Environment settings loading via pydantic-settings
│   ├── database.py        # Database connection pool settings and base model
│   ├── main.py            # FastAPI entry point, routers inclusion, CORS, middleware
│   ├── community/         # Community, safety alerts, and case engine modules
│   │   ├── models/        # SQLAlchemy models (CommunityUser, SafetyAlert, etc.)
│   │   ├── schemas/       # Pydantic validation and serializing schemas
│   │   ├── services/      # Algorithmic engine calculations (CRCE, PICE, CIE, CSAE, ICME)
│   │   └── routes/        # Router endpoints (Cases, Alerts, Users, Reports, etc.)
│   ├── middleware/        # Global exception handling & response standardization wrappers
│   └── utils/             # Log rotation utilities and GS1 barcode parser
├── docs/                  # System technical document logs (Architecture, ERDiagrams, API reference)
├── logs/                  # Rotated logs output directory (application.log and error.log)
├── scripts/               # DB seeding and legacy integration test suites
├── tests/                 # Structured pytest test directories (unit, integration, and api)
├── Dockerfile             # Production multi-stage python build configuration
└── docker-compose.yml     # Multi-container orchestration (FastAPI web, Postgres, pgAdmin)
```

---

## ⚙️ Phase 7 Production-Ready Envelopes

### 1. Global API Envelope Format
All JSON response outputs throughout PGN follow standardized envelopes:

#### Success Format
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": { ... }
}
```

#### Failure Format
```json
{
  "success": false,
  "error": "Error details message",
  "details": { ... }
}
```

### 2. Log Management configuration
All operations (incident reports, credibility boosts, alert escalations, and cases created) write logs into two files under the `logs/` directory:
- `logs/application.log` (Info, Warn levels; max 5MB rotating).
- `logs/error.log` (Error, Critical stack traces; max 5MB rotating).

---

## ⚡ Deployment & Running Guide

### 1. Run via Docker Compose (Recommended)
This starts the PostgreSQL database, FastAPI backend web service, and pgAdmin administration UI in separate connected containers:
```powershell
docker compose up --build -d
```
The backend server will run on `http://localhost:8001/` with healthchecks.

### 2. Local Setup
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Setup Tables**: `python -c "from app.database import Base, engine; from app.models import *; Base.metadata.create_all(engine)"`
3. **Seed Database**: `python scripts/seed_community.py`
4. **Start Server**: `python -m uvicorn app.main:app --port 8001 --reload`

---

## 🧪 Testing

### 1. Run integration end-to-end tests
Runs 48 tests verifying credibility points, clustering joins, alerts auto-resolving, case assignments, notes, evidence logs, and timeline trails:
```powershell
python scripts/test_pgn_endpoints.py
```

### 2. Run pytest suite
Runs pytest unit and integration coverage checks:
```powershell
pytest tests/
```
