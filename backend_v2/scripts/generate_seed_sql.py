"""
generate_seed_sql.py
Generates a complete seed_all_tables.sql file that can be piped
directly into Docker without needing a Python DB connection.
Run: python scripts/generate_seed_sql.py
Then: Get-Content scripts/seed_all_tables.sql | docker exec -i expiry_postgres psql -U expiry_user -d expiry_db
"""
import uuid, random
from datetime import date, timedelta

def uid(): return str(uuid.uuid4())
def sq(s): return s.replace("'", "''") if s else "NULL"
def d(n):  return str(date.today() + timedelta(days=n))
def da(n): return str(date.today() - timedelta(days=n))

lines = ["-- AUTO-GENERATED: seed_all_tables.sql", "-- Idempotent: safe to run multiple times\n"]

# ── PRODUCTS ─────────────────────────────────────────────────
PRODUCTS = [
    ("Amul Taaza Milk 500ml",          "Amul",          "AMUL-TAAZA-500ML",       "8901262010011","EAN13","Dairy",         "Pasteurised toned milk pouch.",             "refrigerated"),
    ("Nestle Everyday Whitener 400g",  "Nestle",        "NESTLE-EW-400G",         "8901058850123","EAN13","Dairy",         "Dairy whitener powder for tea and coffee.", "ambient"),
    ("Mother Dairy Classic Curd 400g", "Mother Dairy",  "MD-CURD-400G",           "8901648004321","EAN13","Dairy",         "Fresh curd requiring cold storage.",        "refrigerated"),
    ("Amul Salted Butter 100g",        "Amul",          "AMUL-BUTTER-100G",       "8901262030019","EAN13","Dairy",         "Salted butter block, 100g.",                "refrigerated"),
    ("Britannia Good Day Cookies 200g","Britannia",     "BRIT-GD-200G",           "8901063160012","EAN13","Snacks",        "Cashew cookies packed for retail.",         "ambient"),
    ("Parle-G Glucose Biscuits 250g",  "Parle",         "PARLE-G-250G",           "8901719101015","EAN13","Snacks",        "Classic glucose biscuits.",                 "ambient"),
    ("Lay''s Classic Salted Chips 52g","Lay's",         "LAYS-CLASSIC-52G",       "8901491100226","EAN13","Snacks",        "Classic salted potato chips.",              "ambient"),
    ("Kurkure Masala Munch 90g",       "Kurkure",       "KURKURE-MASALA-90G",     "8901491501221","EAN13","Snacks",        "Spicy crunchy corn snack.",                 "ambient"),
    ("Coca-Cola Original 750ml",       "Coca-Cola",     "COKE-750ML",             "8901764012342","EAN13","Beverages",     "Carbonated soft drink bottle.",             "ambient"),
    ("Real Mixed Fruit Juice 1L",      "Real",          "REAL-MIXED-1L",          "8901207011123","EAN13","Beverages",     "Packaged mixed fruit juice carton.",        "ambient"),
    ("Tropicana Orange Delight 1L",    "Tropicana",     "TROP-ORANGE-1L",         "8901491200452","EAN13","Beverages",     "Packaged orange fruit beverage.",           "ambient"),
    ("Bisleri Mineral Water 1L",       "Bisleri",       "BISLERI-1L",             "8901207040017","EAN13","Beverages",     "Packaged drinking water 1-litre.",          "ambient"),
    ("Harvest Gold White Bread 400g",  "Harvest Gold",  "HG-WHITE-BREAD-400G",    "8901725180089","EAN13","Bakery",        "Packaged white bread loaf.",                "ambient"),
    ("Britannia Brown Bread 400g",     "Britannia",     "BRIT-BROWN-BREAD-400G",  "8901063019870","EAN13","Bakery",        "Packaged brown bread loaf.",                "ambient"),
    ("Maggi Masala Noodles 70g",       "Maggi",         "MAGGI-MASALA-70G",       "8901058840018","EAN13","Packaged Foods","Instant noodles with masala tastemaker.",   "ambient"),
    ("Aashirvaad Wheat Atta 1kg",      "Aashirvaad",    "AASHIRVAAD-ATTA-1KG",    "8901725123456","EAN13","Packaged Foods","Whole wheat flour pack.",                   "ambient"),
    ("Tata Salt Iodized 1kg",          "Tata",          "TATA-SALT-1KG",          "8904043901017","EAN13","Packaged Foods","Iodized salt packet.",                      "ambient"),
    ("Fortune Sunflower Oil 1L",       "Fortune",       "FORTUNE-SFO-1L",         "8906007280012","EAN13","Packaged Foods","Refined sunflower cooking oil.",            "ambient"),
    ("Dove Cream Beauty Bar 100g",     "Dove",          "DOVE-BAR-100G",          "8901030865432","EAN13","Personal Care", "Moisturizing bathing soap bar.",            "ambient"),
    ("Dettol Antiseptic Liquid 250ml", "Dettol",        "DETTOL-250ML",           "8901396389012","EAN13","Personal Care", "Antiseptic disinfectant liquid.",           "ambient"),
]

prod_ids = [uid() for _ in PRODUCTS]

lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 1. PRODUCTS (20)")
lines.append("-- ═══════════════════════════════════════════")
for pid, (name, brand, sku, barcode, btype, cat, desc, storage) in zip(prod_ids, PRODUCTS):
    lines.append(f"""INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('{pid}','{sq(name)}','{sq(brand)}','{sq(sku)}','{barcode}','{btype}','{cat}','{sq(desc)}','{storage}',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;""")

lines.append("")

# ── BARCODE SCANS (25) ────────────────────────────────────────
scan_ids = [uid() for _ in range(25)]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 2. BARCODE SCANS (25)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(20):
    pid = prod_ids[i]
    barcode = PRODUCTS[i][3]
    lines.append(f"""INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('{scan_ids[i]}','{pid}','{barcode}','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;""")
unknowns = ["9990000000001","9990000000002","9990000000003","9990000000004","9990000000005"]
for i,bc in enumerate(unknowns):
    lines.append(f"""INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('{scan_ids[20+i]}',NULL,'{bc}','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── INVENTORY ITEMS (25) ──────────────────────────────────────
inv_ids = [uid() for _ in range(25)]
expiry_offsets = [-5, 15, 45, 120, None]  # expired, near, priority, good, missing
pipelines = ["PENDING_OCR","OCR_COMPLETED","PENDING_ML_REVIEW","ML_COMPLETED","MANUAL_REVIEW"]
storages  = [PRODUCTS[i % len(PRODUCTS)][7] for i in range(25)]

lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 3. INVENTORY ITEMS (25)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(25):
    pid = prod_ids[i % len(prod_ids)]
    sid = scan_ids[i % 20]
    mfg = da(random.randint(30, 180))
    offset = expiry_offsets[i % 5]
    exp = f"'{d(offset)}'" if offset is not None else "NULL"
    pipeline = pipelines[i % len(pipelines)]
    batch = f"BATCH-{2026001+i}"
    qty = random.randint(1, 50)
    lines.append(f"""INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('{inv_ids[i]}','{pid}','{sid}','{batch}','{mfg}',{exp},'{pipeline}',{qty},'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── PRODUCT IMAGES (30) ───────────────────────────────────────
img_ids = [uid() for _ in range(30)]
img_types = ["front_label","back_label","barcode_close_up","product_photo"]
img_statuses = ["uploaded","ocr_pending","ocr_completed","failed"]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 4. PRODUCT IMAGES (30)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(30):
    pid = prod_ids[i % len(prod_ids)]
    barcode = PRODUCTS[i % len(PRODUCTS)][3]
    itype   = img_types[i % len(img_types)]
    istatus = img_statuses[i % len(img_statuses)]
    fsize   = random.randint(50000, 500000)
    lines.append(f"""INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('{img_ids[i]}','{pid}','/uploads/{barcode}_{i}.jpg','https://cdn.expiry.io/{barcode}_{i}.jpg',{fsize},'image/jpeg','{itype}','{istatus}',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── OCR RESULTS (28) ─────────────────────────────────────────
ocr_ids = [uid() for _ in range(28)]
raw_texts = [
    "MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A",
    "Manufacturing Date: March 2026  Best Before: Sep 2026",
    "Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421",
    "PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45",
    "Label torn -- partial: ...exp 06/2026...",
    "MFG 2026-01-10  EXP 2026-07-10  LOT 9921B",
    "Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221",
]
engines = ["tesseract-5.3","google-vision-v1","aws-textract-v2"]
ocr_statuses = ["pending","completed","completed","completed","failed"]
text_blocks = [
    '[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',
    '[{"label":"Best Before","value":"Sep 2026"}]',
    '[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',
    '[]',
]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 5. OCR RESULTS (28)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(28):
    img_id  = img_ids[i % len(img_ids)]
    inv_id  = inv_ids[i % len(inv_ids)]
    engine  = engines[i % len(engines)]
    status  = ocr_statuses[i % len(ocr_statuses)]
    conf    = round(random.uniform(0.55, 0.99), 4) if status == "completed" else "NULL"
    raw     = sq(raw_texts[i % len(raw_texts)])
    blocks  = text_blocks[i % len(text_blocks)]
    failure = "'OCR engine timeout'" if status == "failed" else "NULL"
    proc_at = "NOW()" if status == "completed" else "NULL"
    lines.append(f"""INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('{ocr_ids[i]}','{img_id}','{inv_id}','{raw}','{engine}','1.0','{blocks}',{conf},'{status}',{failure},{proc_at},NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── STORAGE CONTEXTS (25) ────────────────────────────────────
zones   = ["Zone-A","Zone-B","Cold-Room-1","Cold-Room-2","Frozen-Bay","Ambient-Rack-3"]
s_types = {"refrigerated":"refrigerated","frozen":"frozen","ambient":"ambient"}
wh_ids  = ["WH-DELHI-01","WH-MUMBAI-02","WH-BANGALORE-03"]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 6. STORAGE CONTEXTS (25)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(25):
    inv_id  = inv_ids[i]
    storage = storages[i]
    s_type  = "refrigerated" if storage=="refrigerated" else "frozen" if storage=="frozen" else "ambient"
    temp    = round(random.uniform(2,8),2) if s_type=="refrigerated" else round(random.uniform(-20,-15),2) if s_type=="frozen" else round(random.uniform(18,28),2)
    humid   = round(random.uniform(40,70),2)
    lines.append(f"""INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('{uid()}','{inv_id}','{wh_ids[i%3]}','{zones[i%6]}','A{(i%5)+1}','S{(i%4)+1}','BIN-{100+i}','{s_type}',{temp},{humid},'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;""")
lines.append("")

# ── ML PREDICTIONS (20) ──────────────────────────────────────
decisions = ["ACCEPTED","PRIORITY_SALE","REJECTED","REJECTED","REQUIRES_REVIEW"]
ml_reasons = [
    "Product has sufficient shelf life remaining.",
    "Nearing expiry -- prioritize for immediate sale.",
    "Product is already expired. Do not sell.",
    "Remaining shelf life below minimum threshold.",
    "Confidence too low -- requires human review.",
]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 7. ML PREDICTIONS (20)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(20):
    inv_id    = inv_ids[i]
    offset    = expiry_offsets[i % 5]
    exp_val   = f"'{d(offset)}'" if offset is not None else "NULL"
    remaining = offset if offset is not None else "NULL"
    decision  = decisions[i % len(decisions)]
    conf      = round(random.uniform(0.72, 0.99), 4)
    reason    = sq(ml_reasons[i % len(ml_reasons)])
    lines.append(f"""INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('{uid()}','{inv_id}','expiry-shelf-v2.1','2.1.0',{exp_val},{remaining},'{decision}',{conf},'{reason}','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── MANUAL REVIEWS (10) ──────────────────────────────────────
roles       = ["warehouse_staff","supervisor","qa"]
mr_decisions= ["ACCEPTED","REJECTED","PRIORITY_SALE","ESCALATE_TO_QA"]
escalations = [
    "OCR failed -- label was torn.",
    "ML confidence below threshold.",
    "Conflicting dates found on packaging.",
    "Batch close to expiry -- supervisor review required.",
    "Batch number missing from label.",
]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 8. MANUAL REVIEWS (10)")
lines.append("-- ═══════════════════════════════════════════")
for i in range(10):
    inv_id  = inv_ids[i]
    offset  = expiry_offsets[i % 5]
    corr    = f"'{d((offset or 30) + 2)}'"
    decision= mr_decisions[i % len(mr_decisions)]
    role    = roles[i % len(roles)]
    status  = "completed" if i < 5 else "pending"
    rev_at  = "NOW()" if i < 5 else "NULL"
    esc     = sq(escalations[i % len(escalations)])
    lines.append(f"""INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('{uid()}','{inv_id}','USR-{1000+i}','{role}',{corr},'{decision}','Manually verified batch. Corrected expiry date confirmed.','{esc}','{status}',{rev_at},NOW(),NOW())
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── AUDIT LOGS (40) ──────────────────────────────────────────
event_types = [
    ("product.created",             "product",        "system"),
    ("inventory.intake",            "inventory_item", "service"),
    ("ocr.completed",               "ocr_result",     "service"),
    ("ocr.failed",                  "ocr_result",     "service"),
    ("ml.prediction_received",      "inventory_item", "ml_team"),
    ("manual_review.completed",     "inventory_item", "user"),
    ("status.changed",              "inventory_item", "system"),
    ("barcode.scanned",             "barcode_scan",   "service"),
    ("product.updated",             "product",        "user"),
    ("inventory.flagged_for_review","inventory_item", "system"),
]
lines.append("-- ═══════════════════════════════════════════")
lines.append("-- 9. AUDIT LOGS (40)")
lines.append("-- ═══════════════════════════════════════════")
summaries = [
    "Product registered in catalogue.",
    "Batch received at warehouse intake.",
    "OCR extraction completed successfully.",
    "OCR extraction failed due to engine timeout.",
    "ML prediction returned with decision.",
    "Manual review completed by warehouse staff.",
    "Pipeline status updated to next stage.",
    "Barcode scanned via handheld scanner.",
    "Product details updated by staff.",
    "Item flagged for manual review due to low confidence.",
]
for i in range(40):
    etype, entity_type, actor_type = event_types[i % len(event_types)]
    entity_id = prod_ids[i % len(prod_ids)] if entity_type=="product" else \
                inv_ids[i % len(inv_ids)]   if entity_type=="inventory_item" else \
                ocr_ids[i % len(ocr_ids)]   if entity_type=="ocr_result" else uid()
    summary  = sq(summaries[i % len(summaries)])
    before   = '\'{"status":"PENDING_OCR"}\'' if "status" in summaries[i%10] else "NULL"
    after    = '\'{"status":"OCR_COMPLETED"}\'' if "status" in summaries[i%10] else "NULL"
    ip       = f"10.0.{(i%4)+1}.{(i%20)+1}"
    secs_ago = i * 120
    lines.append(f"""INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('{uid()}','{etype}','{entity_type}','{entity_id}','actor-{1000+(i%10)}','{actor_type}',{before},{after},'{summary}','{ip}','req-{uid()[:8]}',NOW() - INTERVAL '{secs_ago} seconds')
ON CONFLICT DO NOTHING;""")
lines.append("")

# ── WRITE FILE ────────────────────────────────────────────────
out = "scripts/seed_all_tables.sql"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Generated: {out}")
print(f"  products={len(PRODUCTS)}, barcode_scans=25, inventory_items=25")
print(f"  product_images=30, ocr_results=28, storage_contexts=25")
print(f"  ml_predictions=20, manual_reviews=10, audit_logs=40")
print(f"\nRun:")
print(f"  Get-Content scripts/seed_all_tables.sql | docker exec -i expiry_postgres psql -U expiry_user -d expiry_db")
