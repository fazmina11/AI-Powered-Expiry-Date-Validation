# AI-Powered Expiry Date Validation

Backend service for validating packaged products during warehouse / dark-store inventory intake.

Supports barcode-based product lookup, batch creation, manufacturing and expiry date validation, remaining shelf-life calculation, automated inventory decisions, and dashboard monitoring.

> **Phase 1 complete.** ML / OCR integration is not part of this phase — the backend is designed to accept OCR output via `POST /api/v1/validation/manual` when the ML team is ready.

---

## Architecture

```
Client HTTP Request
        │
        ▼
  FastAPI Router  (/api/v1/*)
        │
        ▼
  Service Layer   (business logic, aggregation, decisions)
        │
        ▼
  SQLAlchemy ORM
        │
        ▼
  PostgreSQL (prod) / SQLite (dev)
```

**Key design decisions:**
- Routes contain zero business logic — only HTTP concerns
- All decisions live in `shelf_life_service.evaluate_shelf_life()`
- Validation status derived from `confidence_score` in `validation_service`
- Dashboard aggregations isolated in `dashboard_service`
- All statuses are string constants from `utils/constants.py`

---

## Folder Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app, CORS, lifespan, routers
│   ├── config.py                    # All settings loaded from .env
│   ├── database.py                  # Engine, SessionLocal, Base, get_db
│   ├── models/
│   │   ├── __init__.py              # Registers all models on Base.metadata
│   │   ├── product.py               # Product model
│   │   ├── inventory.py             # InventoryItem model
│   │   └── validation_record.py     # ValidationRecord model
│   ├── schemas/
│   │   ├── product_schema.py        # ProductCreate / Update / Response
│   │   ├── inventory_schema.py      # InventoryIntakeRequest / Response / ListResponse
│   │   ├── validation_schema.py     # ValidationCreate / Response
│   │   └── dashboard_schema.py      # All dashboard response shapes
│   ├── routes/
│   │   ├── product_routes.py        # /api/v1/products
│   │   ├── inventory_routes.py      # /api/v1/inventory
│   │   ├── validation_routes.py     # /api/v1/validation
│   │   └── dashboard_routes.py      # /api/v1/dashboard
│   ├── services/
│   │   ├── product_service.py       # Product CRUD
│   │   ├── inventory_service.py     # Intake orchestration
│   │   ├── shelf_life_service.py    # Pure decision engine
│   │   ├── validation_service.py    # Validation record management
│   │   └── dashboard_service.py     # All aggregation queries
│   └── utils/
│       ├── constants.py             # All status string literals
│       ├── response.py              # success_response / error_response
│       ├── exceptions.py            # All custom exception classes
│       └── logger.py                # Structured application logger
├── tests/
│   ├── conftest.py                  # TestClient + in-memory SQLite fixture
│   ├── test_products.py             # Phase 1.3 — 17 tests
│   ├── test_inventory.py            # Phase 1.5 — 18 tests
│   ├── test_validation.py           # Phase 1.6 — 13 tests
│   ├── test_dashboard.py            # Phase 1.7 — 14 tests
│   └── test_shelf_life_service.py   # Phase 1.4 — 14 tests
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone and enter the backend directory

```bash
git clone <repo-url>
cd AI-Powered-Expiry-Date-Validation/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` — set at minimum:

```env
DATABASE_URL=sqlite:///./expiry_validation.db
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
APP_ENV=development
```

For PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/expiry_db
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Tables are created automatically on first startup when `APP_ENV=development`.  
For production: `alembic upgrade head`

---

## Health Check

```http
GET /health
```

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "env": "development"
}
```

---

## API Documentation

All endpoints are prefixed `/api/v1/`.

### Products — `/api/v1/products`

#### POST /api/v1/products — Create product

**Request**
```json
{
  "name": "Milk Packet",
  "sku": "MILK-500ML",
  "barcode": "8901234567890",
  "category": "Dairy"
}
```

**Response 201**
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": {
    "id": 1, "name": "Milk Packet", "sku": "MILK-500ML",
    "barcode": "8901234567890", "category": "Dairy",
    "image_url": null, "created_at": "...", "updated_at": "..."
  }
}
```

**Error 409**
```json
{"success": false, "message": "A product with this SKU already exists", "error_code": "DUPLICATE_SKU"}
```

---

#### GET /api/v1/products — List all products

| Param | Default | Description |
|-------|---------|-------------|
| `skip` | 0 | Offset |
| `limit` | 50 | Page size |

---

#### GET /api/v1/products/{id} — Get by ID

**Error 404**
```json
{"success": false, "message": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
```

---

#### GET /api/v1/products/barcode/{barcode} — Barcode lookup

```http
GET /api/v1/products/barcode/8901234567890
```

---

#### PUT /api/v1/products/{id} — Update product

All fields optional. Only supplied fields are updated.

---

#### DELETE /api/v1/products/{id} — Delete product

**Response 200**
```json
{"success": true, "message": "Product deleted successfully", "data": null}
```

---

### Inventory — `/api/v1/inventory`

#### POST /api/v1/inventory/intake — Intake a batch

**Request**
```json
{
  "barcode": "8901234567890",
  "batch_number": "BATCH001",
  "manufacturing_date": "2026-05-01",
  "expiry_date": "2026-11-01"
}
```

**Response 201 — ACCEPTED**
```json
{
  "success": true,
  "message": "Inventory item processed successfully",
  "data": {
    "id": 1, "product_id": 1, "batch_number": "BATCH001",
    "manufacturing_date": "2026-05-01", "expiry_date": "2026-11-01",
    "remaining_days": 161, "status": "ACCEPTED",
    "decision_reason": "Product has sufficient shelf life.",
    "created_at": "..."
  }
}
```

**Response 201 — REJECTED**
```json
{
  "success": true,
  "message": "Inventory item processed successfully",
  "data": {"status": "REJECTED", "remaining_days": 5, ...}
}
```

Decision rules:

| Condition | Status |
|-----------|--------|
| `expiry_date` missing | `MANUAL_REVIEW` |
| `expiry_date < manufacturing_date` | `INVALID_DATE` |
| `expiry_date < today` | `REJECTED` |
| `remaining_days < 30` | `REJECTED` |
| `30 ≤ remaining_days ≤ 60` | `PRIORITY_SALE` |
| `remaining_days > 60` | `ACCEPTED` |

---

#### GET /api/v1/inventory — List all items

Returns `{total, items[]}`.

#### GET /api/v1/inventory/{id} — Get by ID

#### GET /api/v1/inventory/status/{status} — Filter by status

Valid values: `ACCEPTED`, `PRIORITY_SALE`, `REJECTED`, `MANUAL_REVIEW`, `INVALID_DATE`  
Case-insensitive. Returns `{total, items[]}`.

---

### Validation — `/api/v1/validation`

#### POST /api/v1/validation/manual — Store validation record

OCR integration point. The ML team will POST extracted data here.

**Request**
```json
{
  "inventory_item_id": 1,
  "raw_text": "MFG 01/05/2026 EXP 01/11/2026",
  "extracted_mfg_date": "2026-05-01",
  "extracted_expiry_date": "2026-11-01",
  "confidence_score": 0.98
}
```

**Response 201**
```json
{
  "success": true,
  "message": "Validation record stored",
  "data": {"validation_status": "VALID", "confidence_score": 0.98, ...}
}
```

Validation status rules:

| Condition | Status |
|-----------|--------|
| `extracted_expiry_date` missing | `MANUAL_REVIEW` |
| `confidence_score` missing | `MANUAL_REVIEW` |
| `confidence_score >= 0.80` | `VALID` |
| `confidence_score < 0.80` | `LOW_CONFIDENCE` |

#### GET /api/v1/validation/{inventory_item_id} — Get records for item

Returns all validation records newest-first. Empty list if none exist.

---

### Dashboard — `/api/v1/dashboard`

#### GET /api/v1/dashboard/summary

```json
{
  "success": true,
  "message": "Dashboard summary retrieved",
  "data": {
    "total_products": 125,
    "total_inventory_items": 2500,
    "accepted_count": 1900,
    "priority_sale_count": 300,
    "rejected_count": 150,
    "manual_review_count": 100,
    "invalid_date_count": 50,
    "valid_validation_count": 2100,
    "low_confidence_count": 250
  }
}
```

#### GET /api/v1/dashboard/inventory-breakdown

Counts per inventory decision status.

#### GET /api/v1/dashboard/validation-breakdown

Counts per validation status.

#### GET /api/v1/dashboard/recent-inventory?limit=10

Most recently created inventory items, newest first.

#### GET /api/v1/dashboard/recent-validations?limit=10

Most recently created validation records, newest first.

#### GET /api/v1/dashboard/alerts

All items needing attention (REJECTED, INVALID_DATE, MANUAL_REVIEW).

```json
{
  "success": true,
  "message": "Alerts retrieved",
  "data": {"count": 32, "items": [...]}
}
```

---

## Running Tests

```bash
# From the backend/ directory
cd backend

# Run all 77 tests
pytest

# Verbose output
pytest -v

# Specific file
pytest tests/test_shelf_life_service.py -v

# With coverage
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

**Expected output:**
```
77 passed in ~2s
```

Tests use an **isolated in-memory SQLite database** — no setup required, no data persists between runs.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `sqlite:///./expiry_validation.db` | SQLAlchemy connection string |
| `SECRET_KEY` | Yes | — | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT token lifetime |
| `WARNING_DAYS` | No | `60` | Days threshold → PRIORITY_SALE |
| `REJECT_DAYS` | No | `30` | Days threshold → REJECTED |
| `APP_ENV` | No | `development` | `development` / `staging` / `production` |

---

## Notes for Frontend & ML Teams

**Frontend team:**
- All endpoints at `/api/v1/*`
- Consistent envelope: `{"success": bool, "message": str, "data": any}`
- Errors in `detail.error_code` for machine-readable handling
- Interactive docs: `GET /docs`

**ML / OCR team:**
- Push extracted label data to `POST /api/v1/validation/manual`
- Fields: `raw_text`, `extracted_mfg_date`, `extracted_expiry_date`, `confidence_score`
- `validation_status` is derived automatically from `confidence_score`
- No code changes needed — the endpoint contract is already defined

**For production deployment:**
- Set `APP_ENV=production` (disables auto `create_all`)
- Run `alembic upgrade head` before starting
- Replace `SECRET_KEY` default with a generated value
- Restrict `allow_origins` in CORS middleware
