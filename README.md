# AI-Powered Expiry Date Validation

Full-stack expiry-date validation system for retail, warehouse, and dark-store inventory operations. The project combines barcode lookup, OCR-assisted label scanning, product intelligence, inventory intake, alerts, manual review flows, and a dashboard UI.

The current codebase contains two backend tracks:

- `backend_v2/` is the active full-stack API used by the Next.js frontend.
- `api/`, `pipeline/`, and `demo/` are the legacy OCR/scanner prototype used by `Start_All.bat`.
- `backend/` is the original Phase 1 backend kept for reference and tests.

## What We Have Built So Far

- Next.js dashboard frontend in `Frontend/`.
- FastAPI Phase 2 backend in `backend_v2/`.
- PostgreSQL schema, seed scripts, pgAdmin setup, and SQL dump under `backend_v2/`.
- Authentication routes for signup, login, and current-user lookup.
- Product catalogue and barcode lookup routes.
- OCR upload route and image upload/static-file support.
- Inventory intake, list, edit, delete, and dashboard stats support.
- Alerts and manual-review APIs for failed scans, missing expiry data, unknown barcodes, and human correction.
- Frontend pages for landing, auth, dashboard, scan, inventory, alerts, and settings.
- Frontend API service wired to `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_AUTH_URL`.
- Legacy OCR pipeline with EasyOCR/OpenCV date extraction under `pipeline/` and `backend_v2/app/services/`.
- Desktop and Streamlit demo tools under `demo/`.
- Batch launch scripts for the legacy scanner flow.

## Repository Structure

```text
.
|-- Frontend/                  Next.js 14 app, dashboard UI, auth pages, scanner UI
|-- backend_v2/                Active FastAPI API, PostgreSQL models, routes, services
|-- backend_v2/scripts/        Schema and seed utilities
|-- backend_v2/dev_tools/      Webcam/OCR experiments and debugging tools
|-- backend/                   Original Phase 1 FastAPI backend and tests
|-- api/                       Lightweight legacy OCR API
|-- pipeline/                  OCR/date parsing inference prototype
|-- demo/                      Streamlit and desktop scanner prototype
|-- tests/                     OCR pipeline test data and evaluation scripts
|-- Start_All.bat              Legacy launcher for API + Streamlit + desktop scanner
|-- Launch_Scanner.bat         Legacy desktop scanner launcher
```

## Main Services And Ports

| Service | Path | Default Port | Purpose |
| --- | --- | ---: | --- |
| Frontend | `Frontend/` | `3000` | User-facing Next.js app |
| Active backend | `backend_v2/` | `8001` | Dashboard, auth, product, OCR, inventory, alerts, reviews |
| PostgreSQL | `backend_v2/docker-compose.yml` | `5434` -> `5432` | Local database |
| pgAdmin | `backend_v2/docker-compose.yml` | `5050` | Database browser |
| Legacy OCR API | `api/main.py` | `8000` | Prototype image validation endpoint |
| Legacy Streamlit dashboard | `demo/app.py` | `8501` | Prototype dashboard |

## Prerequisites

- Python 3.11+ recommended.
- Node.js 18+ recommended.
- Docker Desktop for PostgreSQL and pgAdmin.
- Git.
- Optional: ngrok or Cloudflare Tunnel for public testing.
- Optional: a webcam for live scanner demos.

## Clone

```bash
git clone https://github.com/Harish-0412/AI-Powered-Expiry-Date-Validation.git
cd AI-Powered-Expiry-Date-Validation
```

## Start The Active Full-Stack App

Run these from separate terminals.

Quick local startup checklist:

1. Start PostgreSQL from `backend_v2/`.
2. Start the FastAPI backend on port `8001`.
3. Start the Next.js frontend on port `3000`.
4. Open `http://localhost:3000`.

The frontend does not connect to PostgreSQL directly. Browser code calls the FastAPI backend, and FastAPI connects to PostgreSQL with `DATABASE_URL`.

### 1. Start PostgreSQL And pgAdmin

```bash
cd backend_v2
docker compose up -d
```

Database defaults:

```env
POSTGRES_USER=expiry_user
POSTGRES_PASSWORD=expiry_pass
POSTGRES_DB=expiry_db
POSTGRES_PORT=5434
```

pgAdmin:

- URL: `http://localhost:5050`
- Email: `admin@expiryvalidation.com`
- Password: `admin123`

### 2. Configure The Active Backend

Create `backend_v2/.env`:

```env
DATABASE_URL=postgresql://expiry_user:expiry_pass@localhost:5434/expiry_db
APP_ENV=development
APP_VERSION=2.0.0
SECRET_KEY=change_this_secret_key_phase2
UPLOAD_DIR=./uploads
ML_WEBHOOK_URL=
```

For a stronger local secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Install And Start The Active Backend

```bash
cd backend_v2
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Backend URLs:

- Health: `http://localhost:8001/health`
- Swagger docs: `http://localhost:8001/docs`
- Static uploads: `http://localhost:8001/static/uploads/...`

### 4. Seed Demo Data

The database schema is mounted automatically when the PostgreSQL container starts for the first time. If you need seed data, run one or more of the scripts from `backend_v2/`:

```bash
python scripts/create_tables.py
python scripts/seed_products.py
python scripts/seed_mock_data.py
python scripts/seed_alerts_reviews.py
```

There are also SQL seed files in `backend_v2/scripts/`:

```bash
psql "postgresql://expiry_user:expiry_pass@localhost:5434/expiry_db" -f scripts/seed_all_tables.sql
```

### 5. Configure And Start The Frontend

Create `Frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
NEXT_PUBLIC_SCAN_URL=http://localhost:8001/api/scan
```

Then start Next.js:

```bash
cd Frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:3000`

### How The Frontend, Backend, And Database Connect

```text
Next.js frontend
  -> NEXT_PUBLIC_API_URL / NEXT_PUBLIC_AUTH_URL / NEXT_PUBLIC_SCAN_URL
  -> FastAPI backend on http://localhost:8001
  -> DATABASE_URL
  -> PostgreSQL on localhost:5434
```

Use these local values for the active stack:

| Layer | Setting | Local value |
| --- | --- | --- |
| Frontend API calls | `NEXT_PUBLIC_API_URL` | `http://localhost:8001/api/v1` |
| Frontend auth calls | `NEXT_PUBLIC_AUTH_URL` | `http://localhost:8001` |
| Frontend scan-session calls | `NEXT_PUBLIC_SCAN_URL` | `http://localhost:8001/api/scan` |
| Backend database connection | `DATABASE_URL` | `postgresql://expiry_user:expiry_pass@localhost:5434/expiry_db` |

If the frontend loads but dashboard data is empty or requests fail, check these in order:

1. PostgreSQL is running: `cd backend_v2 && docker compose ps`
2. Backend health works: open `http://localhost:8001/health`
3. Frontend env values are present in `Frontend/.env.local`
4. Next.js was restarted after changing `.env.local`
5. The browser network tab shows calls going to `localhost:8001`

## Start The Public Tunnel

Use a tunnel when you want to test the app from another device, share a demo URL, or test camera access over HTTPS.

### Option A: ngrok

Tunnel the frontend:

```bash
ngrok http 3000
```

Tunnel the backend:

```bash
ngrok http 8001
```

If the backend tunnel URL is `https://your-backend.ngrok-free.app`, update `Frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://your-backend.ngrok-free.app/api/v1
NEXT_PUBLIC_AUTH_URL=https://your-backend.ngrok-free.app
NEXT_PUBLIC_SCAN_URL=https://your-backend.ngrok-free.app/api/scan
```

Restart the frontend after changing `.env.local`.

### Option B: Cloudflare Tunnel

Tunnel the frontend:

```bash
cloudflared tunnel --url http://localhost:3000
```

Tunnel the backend:

```bash
cloudflared tunnel --url http://localhost:8001
```

Use the generated backend URL in `Frontend/.env.local` the same way as the ngrok example.

## Start The Legacy OCR Prototype

The legacy flow is useful for testing the original OCR pipeline, Streamlit dashboard, and desktop scanner.

Install root-level Python dependencies:

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Start everything on Windows:

```bat
Start_All.bat
```

This starts:

- Legacy OCR API on `http://localhost:8000`
- Streamlit dashboard on `http://localhost:8501`
- Desktop scanner from `demo/desktop_app.py`

Or start each service manually:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
python -m streamlit run demo/app.py --server.port 8501
python demo/desktop_app.py
```

Legacy OCR endpoints:

- `POST /validate`
- `POST /validate/batch`

## Webcam And OCR Experiments

Extra scanner tools live in `backend_v2/dev_tools/`.

```bash
cd backend_v2
python dev_tools/webcam_scanner.py
```

Useful files:

- `app/services/enhanced_preprocessing.py`
- `app/services/standalone_date_extractor.py`
- `app/services/enhanced_ocr_pipeline.py`
- `app/services/paddle_ocr_service.py`
- `dev_tools/test_ocr.py`
- `dev_tools/test_combination_pipeline.py`

Supported date extraction examples include:

- `DD/MM/YYYY`
- `MM/DD/YYYY`
- `YYYY-MM-DD`
- `DD MMM YYYY`
- `MMM DD YYYY`
- short-year variants such as `DD/MM/YY`

Recognized label terms include `MFG`, `MFD`, `PKD`, `PACKED`, `EXP`, `EXPIRY`, `BEST BEFORE`, `USE BY`, `BATCH`, and `LOT`.

## Active Backend API Overview

Base URL:

```text
http://localhost:8001
```

Important routes:

| Area | Route |
| --- | --- |
| Health | `GET /health` |
| Auth | `/auth/signup`, `/auth/login`, `/auth/me` |
| OCR | `/api/v1/ocr/*` |
| Product/barcode | `/api/v1/products/*` |
| Inventory | `/api/v1/inventory/*` |
| Alerts | `/api/v1/alerts/*` |
| Reviews | `/api/v1/reviews/*` |
| Scan sessions | `/api/v1/session/*` |
| Scan pipeline | `/api/scan/*` |
| Product lookup | `GET /api/v1/products/search` |
| Product questions | `POST /api/v1/products/ask` |

Open `http://localhost:8001/docs` for the exact request and response schemas generated by FastAPI.

## Frontend Overview

Important frontend paths:

- `/` - landing page
- `/login` - login
- `/signup` - signup
- `/dashboard` - dashboard home
- `/dashboard/scan` - camera/image scan workflow
- `/dashboard/inventory` - inventory list and edit workflow
- `/dashboard/alerts` - alert and manual review workflow
- `/dashboard/settings` - settings page

Important frontend service files:

- `Frontend/services/apiService.ts`
- `Frontend/services/scanService.ts`
- `Frontend/hooks/useCamera.ts`
- `Frontend/hooks/useBarcodeScanner.ts`
- `Frontend/hooks/useOCR.ts`

## Testing

Original backend tests:

```bash
cd backend
pip install -r requirements.txt
pytest
```

OCR pipeline tests:

```bash
pytest tests
```

Frontend build check:

```bash
cd Frontend
npm run build
```

## Common Troubleshooting

### Frontend cannot reach backend

Check that the backend is running on port `8001`, then confirm:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
```

Restart `npm run dev` after changing `.env.local`.

### Database connection is unavailable

Start Docker services:

```bash
cd backend_v2
docker compose up -d
```

Then verify the backend `DATABASE_URL` uses port `5434` on the host:

```env
DATABASE_URL=postgresql://expiry_user:expiry_pass@localhost:5434/expiry_db
```

### Camera does not open

- Close other apps using the webcam.
- Allow camera permissions in the browser or OS.
- Use HTTPS through ngrok or Cloudflare Tunnel when testing camera access on another device.

### OCR accuracy is low

- Improve lighting.
- Avoid glare on packaging.
- Hold the label steady and close to the camera.
- Try the enhanced OCR scripts in `backend_v2/dev_tools/`.

## Development Notes

- Do not commit `.env`, `.env.local`, database files, uploads, virtual environments, `.next`, or `node_modules`.
- `backend_v2` is the active API target for the frontend.
- `api/`, `pipeline/`, and `demo/` remain useful for OCR experiments and legacy demos.
- The project currently allows broad CORS in development. Lock this down before production deployment.
- Replace default secrets before any hosted deployment.
