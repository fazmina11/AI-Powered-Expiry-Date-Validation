# AI-Powered Expiry Date Validation System

An AI-powered system designed to automate grocery and product expiry date validation during dark-store inventory intake. The system leverages **Computer Vision**, **OCR (PaddleOCR)**, and **Large Language Models (Gemini API)** to extract label information and determine product shelf-life rules.

---

## 🛠️ Summary of Completed Features (As of Today)

### 1. Unified Multi-Service Docker Architecture
- Dockerized the entire Next.js Frontend (`my-frontend` at port 3000) and multi-process FastAPI Backend (`my-backend` at ports 8000 and 8050).
- Configured PostgreSQL container (`expiry_postgres` at port 5433) and pgAdmin (`expiry_pgadmin` at port 5050).

### 2. Teammate Model Schema Integration (Option A)
- Synced codebase with remote teammate updates containing Pydantic schemas, operation models, and dashboard section modules.
- Re-initialized a complete database layout containing all **26 database tables** mapped to the SQLAlchemy entities.
- Seeded **56 products** (including grocery and regional South Indian items) into the database catalogue for lookups.

### 3. OCR Performance Tuning
- Disabled document-layout warping correction (`UVDoc`) inside the PaddleOCR pipeline (`use_textline_orientation=False`).
- **Result**: Reduced OCR initialization startup time from several minutes to under **3 seconds** by eliminating model dynamic C++ compiles and weight downloads.

### 4. End-to-End Persistence Pipeline
- Completed field mappings inside the scanner (`detected_mfg_text`, `detected_expiry_text`, `detected_ingredients_text`, `date_parse_confidence`).
- Verified that product scanning successfully processes OCR, queries catalog metadata, uses Gemini API for date correction, and writes directly to the PostgreSQL `ocr_results` and `inventory_items` tables.

---

## 🗄️ Database Table Layout (26 Tables)

The database schema matches the teammate's models exactly:
```
 Schema |               Name               | Type  |    Owner    
--------+----------------------------------+-------+-------------
 public | audit_logs                       | table | expiry_user
 public | barcode_scans                    | table | expiry_user
 public | external_product_cache           | table | expiry_user
 public | external_product_enrichment_logs | table | expiry_user
 public | inventory_items                  | table | expiry_user
 public | inventory_movements              | table | expiry_user
 public | manual_reviews                   | table | expiry_user
 public | ml_predictions                   | table | expiry_user
 public | ocr_results                      | table | expiry_user
 public | product_allergens                | table | expiry_user
 public | product_identifiers              | table | expiry_user
 public | product_images                   | table | expiry_user
 public | product_ingredients              | table | expiry_user
 public | product_lookup_logs              | table | expiry_user
 public | product_nutrition                | table | expiry_user
 public | product_question_logs            | table | expiry_user
 public | product_storage_requirements     | table | expiry_user
 public | products                         | table | expiry_user
 public | scan_alerts                      | table | expiry_user
 public | scan_sessions                    | table | expiry_user
 public | storage_contexts                 | table | expiry_user
 public | storage_locations                | table | expiry_user
 public | suppliers                        | table | expiry_user
 public | unknown_product_requests         | table | expiry_user
 public | users                            | table | expiry_user
 public | warehouses                       | table | expiry_user
```

---

## 🚦 How to Run & Verify

### 1. Show All Database Tables
Verify tables inside the PostgreSQL container:
```powershell
docker exec -i expiry_postgres psql -U expiry_user -d expiry_db -c "\dt"
```

### 2. Access the Scanning Interface
Open your web browser:
- **Web Scanner Dashboard**: `http://localhost:8050`
- **Main Frontend**: `http://localhost:3000`

### 3. Trigger a Product Scan
Upload a label image (e.g. `AI_expiry_date/AI_expiry_date/backend_v2/uploads/labels/roi_crop_test.jpg`) or use the webcam, then click **Scan/Upload**.

### 4. Verify Database Persistence

Verify OCR details:
```powershell
docker exec -i expiry_postgres psql -U expiry_user -d expiry_db -c "SELECT id, ocr_engine, raw_text, detected_mfg_text, detected_expiry_text, date_parse_confidence FROM ocr_results ORDER BY created_at DESC LIMIT 5;"
```

Verify Inventory intake item:
```powershell
docker exec -i expiry_postgres psql -U expiry_user -d expiry_db -c "SELECT id, product_id, batch_number, manufacturing_date, expiry_date FROM inventory_items ORDER BY created_at DESC LIMIT 5;"
```
