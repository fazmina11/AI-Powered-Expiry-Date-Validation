"""
build_seed_sql.py
=================
Reads actual product UUIDs from PostgreSQL (via docker exec),
then generates scripts/seed_linked.sql with correctly wired
foreign keys across all 9 tables.

Run:
    python scripts/build_seed_sql.py
    Get-Content scripts/seed_linked.sql | docker exec -i expiry_postgres psql -U expiry_user -d expiry_db
"""

import subprocess
import uuid
import random
from datetime import date, timedelta

# ── helpers ──────────────────────────────────────────────────
def uid():
    return str(uuid.uuid4())

def future(n):
    return str(date.today() + timedelta(days=n))

def past(n):
    return str(date.today() - timedelta(days=n))

def sq(s):
    """Escape single quotes for SQL."""
    return s.replace("'", "''") if s else ""


# ── Step 1: pull real product UUIDs from the running container ─
def fetch_products():
    result = subprocess.run(
        [
            "docker", "exec", "expiry_postgres",
            "psql", "-U", "expiry_user", "-d", "expiry_db",
            "-t", "-A", "-F", "|",
            "-c",
            "SELECT id, sku, barcode, COALESCE(default_storage_type,'ambient') "
            "FROM products ORDER BY created_at LIMIT 25;"
        ],
        capture_output=True, text=True
    )
    rows = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if "|" in line:
            parts = line.split("|")
            if len(parts) == 4:
                rows.append({
                    "id":      parts[0].strip(),
                    "sku":     parts[1].strip(),
                    "barcode": parts[2].strip(),
                    "storage": parts[3].strip() or "ambient",
                })
    return rows


# ── Step 2: build SQL ─────────────────────────────────────────
def build_sql(products):
    lines = []
    lines.append("BEGIN;")
    lines.append("")

    # ── BARCODE SCANS ─────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 2. BARCODE SCANS  (20 resolved + 5 unresolved)")
    lines.append("-- ════════════════════════════════════════")
    scan_ids = []
    for p in products[:20]:
        sid = uid()
        scan_ids.append(sid)
        lines.append(
            f"INSERT INTO barcode_scans "
            f"(id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at) "
            f"VALUES ('{sid}','{p['id']}','{p['barcode']}','EAN13','handheld_scanner','resolved',NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )

    unknowns = ["9990000000001","9990000000002","9990000000003","9990000000004","9990000000005"]
    for bc in unknowns:
        sid = uid()
        lines.append(
            f"INSERT INTO barcode_scans "
            f"(id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at) "
            f"VALUES ('{sid}',NULL,'{bc}','EAN13','mobile_app','unresolved',"
            f"'Barcode not found in catalogue',NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── INVENTORY ITEMS ───────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 3. INVENTORY ITEMS  (25 batches)")
    lines.append("-- ════════════════════════════════════════")
    inv_ids  = []
    pipelines = ["PENDING_OCR","OCR_COMPLETED","PENDING_ML_REVIEW","ML_COMPLETED","MANUAL_REVIEW"]
    expiry_days = [-5, 15, 45, 120, None]   # expired, near, priority, good, missing

    for i in range(25):
        iid       = uid()
        inv_ids.append(iid)
        p         = products[i % len(products)]
        sid       = scan_ids[i % len(scan_ids)]
        pipeline  = pipelines[i % len(pipelines)]
        mfg       = past(random.randint(30, 180))
        offset    = expiry_days[i % len(expiry_days)]
        exp_val   = f"'{future(offset)}'" if offset is not None else "NULL"
        qty       = random.randint(1, 50)
        batch     = f"BATCH-{2026001 + i}"
        lines.append(
            f"INSERT INTO inventory_items "
            f"(id,product_id,barcode_scan_id,batch_number,manufacturing_date,"
            f"expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at) "
            f"VALUES ('{iid}','{p['id']}','{sid}','{batch}','{mfg}',{exp_val},"
            f"'{pipeline}',{qty},'units',NOW(),NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── PRODUCT IMAGES ────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 4. PRODUCT IMAGES  (30 uploads)")
    lines.append("-- ════════════════════════════════════════")
    img_ids    = []
    img_types  = ["front_label","back_label","barcode_close_up","product_photo","side_label"]
    img_status = ["uploaded","ocr_pending","ocr_completed","uploaded","failed"]

    for i in range(30):
        iid    = uid()
        img_ids.append(iid)
        p      = products[i % len(products)]
        itype  = img_types[i % len(img_types)]
        status = img_status[i % len(img_status)]
        fsize  = random.randint(50000, 500000)
        lines.append(
            f"INSERT INTO product_images "
            f"(id,product_id,file_path,file_url,file_size_bytes,mime_type,"
            f"image_type,processing_status,uploaded_at,created_at,updated_at) "
            f"VALUES ('{iid}','{p['id']}','/uploads/{p['barcode']}_{i}.jpg',"
            f"'https://cdn.expiry.io/{p['barcode']}_{i}.jpg',{fsize},'image/jpeg',"
            f"'{itype}','{status}',NOW(),NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── OCR RESULTS ───────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 5. OCR RESULTS  (28 extractions)")
    lines.append("-- ════════════════════════════════════════")
    raw_texts = [
        "MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A",
        "Manufacturing Date: March 2026  Best Before: Sep 2026",
        "Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421",
        "PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45",
        "Label torn -- partial text only: ...exp 06/2026...",
        "MFG 2026-01-10  EXP 2026-07-10  LOT 9921B",
        "Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221",
    ]
    engines    = ["tesseract-5.3","google-vision-v1","aws-textract-v2"]
    ocr_status = ["pending","completed","completed","completed","failed"]
    blocks     = [
        '[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',
        '[{"label":"Best Before","value":"Sep 2026"}]',
        '[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',
        '[]',
    ]

    ocr_ids = []
    for i in range(28):
        oid      = uid()
        ocr_ids.append(oid)
        img_id   = img_ids[i % len(img_ids)]
        inv_id   = inv_ids[i % len(inv_ids)]
        engine   = engines[i % len(engines)]
        status   = ocr_status[i % len(ocr_status)]
        conf     = round(random.uniform(0.55, 0.99), 4) if status == "completed" else "NULL"
        raw      = sq(raw_texts[i % len(raw_texts)])
        block    = blocks[i % len(blocks)].replace("'", "''")
        failure  = "'OCR engine timeout'" if status == "failed" else "NULL"
        proc_at  = "NOW()" if status != "pending" else "NULL"
        lines.append(
            f"INSERT INTO ocr_results "
            f"(id,product_image_id,inventory_item_id,raw_text,ocr_engine,"
            f"ocr_engine_version,extracted_text_blocks,overall_confidence,"
            f"ocr_status,failure_reason,processed_at,created_at,updated_at) "
            f"VALUES ('{oid}','{img_id}','{inv_id}','{raw}','{engine}',"
            f"'1.0','{block}',{conf},'{status}',{failure},{proc_at},NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── STORAGE CONTEXTS ──────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 6. STORAGE CONTEXTS  (25 records)")
    lines.append("-- ════════════════════════════════════════")
    zones   = ["Zone-A","Zone-B","Cold-Room-1","Cold-Room-2","Frozen-Bay","Ambient-Rack-3"]
    wh_ids  = ["WH-DELHI-01","WH-MUMBAI-02","WH-BANGALORE-03"]

    for i, inv_id in enumerate(inv_ids):
        storage = products[i % len(products)]["storage"]
        s_type  = "refrigerated" if storage == "refrigerated" else \
                  "frozen"       if storage == "frozen"       else "ambient"
        temp = (round(random.uniform(2, 8), 2)     if s_type == "refrigerated" else
                round(random.uniform(-20, -15), 2) if s_type == "frozen"       else
                round(random.uniform(18, 28), 2))
        humid = round(random.uniform(40, 70), 2)
        lines.append(
            f"INSERT INTO storage_contexts "
            f"(id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,"
            f"storage_type,temperature_celsius,humidity_percent,notes,"
            f"recorded_at,created_at,updated_at) "
            f"VALUES ('{uid()}','{inv_id}','{wh_ids[i%3]}','{zones[i%6]}',"
            f"'A{(i%5)+1}','S{(i%4)+1}','BIN-{100+i}','{s_type}',{temp},{humid},"
            f"'Auto-recorded on intake. Temp/humidity from IoT sensor.',"
            f"NOW(),NOW(),NOW()) "
            f"ON CONFLICT (inventory_item_id) DO NOTHING;"
        )
    lines.append("")

    # ── ML PREDICTIONS ────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 7. ML PREDICTIONS  (20 records)")
    lines.append("-- ════════════════════════════════════════")
    decisions = ["ACCEPTED","PRIORITY_SALE","REJECTED","REJECTED","REQUIRES_REVIEW"]
    ml_reasons = [
        "Product has sufficient shelf life remaining.",
        "Nearing expiry -- prioritize for immediate sale.",
        "Product is already expired. Do not sell.",
        "Remaining shelf life below reject threshold.",
        "Confidence too low -- requires human review.",
    ]

    for i in range(20):
        inv_id   = inv_ids[i]
        decision = decisions[i % len(decisions)]
        offset   = expiry_days[i % len(expiry_days)]
        exp_val  = f"'{future(offset)}'" if offset is not None else "NULL"
        rem      = str(offset) if offset is not None else "NULL"
        conf     = round(random.uniform(0.72, 0.99), 4)
        reason   = sq(ml_reasons[i % len(ml_reasons)])
        lines.append(
            f"INSERT INTO ml_predictions "
            f"(id,inventory_item_id,model_name,model_version,"
            f"predicted_expiry_date,predicted_remaining_days,"
            f"predicted_decision,decision_confidence,decision_reason,"
            f"prediction_status,predicted_at,created_at,updated_at) "
            f"VALUES ('{uid()}','{inv_id}','expiry-shelf-v2.1','2.1.0',"
            f"{exp_val},{rem},'{decision}',{conf},'{reason}',"
            f"'completed',NOW(),NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── MANUAL REVIEWS ────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 8. MANUAL REVIEWS  (10 records)")
    lines.append("-- ════════════════════════════════════════")
    roles       = ["warehouse_staff","supervisor","qa"]
    mr_decisions= ["ACCEPTED","REJECTED","PRIORITY_SALE","ESCALATE_TO_QA"]
    escalations = [
        "OCR failed -- label was torn and unreadable.",
        "ML confidence 0.43 -- below acceptance threshold.",
        "Conflicting manufacturing and expiry dates on label.",
        "Batch nearing expiry -- supervisor review required.",
        "Batch number missing from product label.",
    ]

    for i in range(10):
        inv_id   = inv_ids[i]
        offset   = expiry_days[i % len(expiry_days)]
        corr_exp = f"'{future((offset or 30) + 2)}'"
        decision = mr_decisions[i % len(mr_decisions)]
        role     = roles[i % len(roles)]
        status   = "completed" if i < 5 else "pending"
        rev_at   = "NOW()" if i < 5 else "NULL"
        esc      = sq(escalations[i % len(escalations)])
        lines.append(
            f"INSERT INTO manual_reviews "
            f"(id,inventory_item_id,reviewer_id,reviewer_role,"
            f"corrected_expiry_date,human_decision,review_notes,"
            f"escalation_reason,review_status,reviewed_at,created_at,updated_at) "
            f"VALUES ('{uid()}','{inv_id}','USR-{1000+i}','{role}',"
            f"{corr_exp},'{decision}',"
            f"'Manually verified batch. Corrected expiry date confirmed.',"
            f"'{esc}','{status}',{rev_at},NOW(),NOW()) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")

    # ── AUDIT LOGS ────────────────────────────────────────────
    lines.append("-- ════════════════════════════════════════")
    lines.append("-- 9. AUDIT LOGS  (40 events)")
    lines.append("-- ════════════════════════════════════════")
    events = [
        ("product.created",              "product",        "system"),
        ("inventory.intake",             "inventory_item", "service"),
        ("ocr.completed",                "ocr_result",     "service"),
        ("ocr.failed",                   "ocr_result",     "service"),
        ("ml.prediction_received",       "inventory_item", "ml_team"),
        ("manual_review.completed",      "inventory_item", "user"),
        ("status.changed",               "inventory_item", "system"),
        ("barcode.scanned",              "barcode_scan",   "service"),
        ("product.updated",              "product",        "user"),
        ("inventory.flagged_for_review", "inventory_item", "system"),
    ]
    summaries = [
        "Product registered in catalogue.",
        "Batch received at warehouse intake.",
        "OCR extraction completed successfully.",
        "OCR extraction failed due to engine timeout.",
        "ML prediction returned with decision ACCEPTED.",
        "Manual review completed by warehouse staff.",
        "Pipeline status updated to next stage.",
        "Barcode scanned via handheld scanner.",
        "Product details updated by staff.",
        "Item flagged for manual review due to low confidence.",
    ]

    for i in range(40):
        etype, entity_type, actor_type = events[i % len(events)]
        entity_id = (products[i % len(products)]["id"] if entity_type == "product"
                     else inv_ids[i % len(inv_ids)]   if entity_type == "inventory_item"
                     else ocr_ids[i % len(ocr_ids)]   if entity_type == "ocr_result"
                     else uid())
        summary  = sq(summaries[i % len(summaries)])
        before   = "'{\"status\":\"PENDING_OCR\"}'" if "status" in summary else "NULL"
        after    = "'{\"status\":\"OCR_COMPLETED\"}'" if "status" in summary else "NULL"
        ip       = f"10.0.{(i%4)+1}.{(i%20)+1}"
        secs_ago = i * 120
        lines.append(
            f"INSERT INTO audit_logs "
            f"(id,event_type,entity_type,entity_id,actor_id,actor_type,"
            f"before_state,after_state,change_summary,ip_address,request_id,occurred_at) "
            f"VALUES ('{uid()}','{etype}','{entity_type}','{entity_id}',"
            f"'actor-{1000+(i%10)}','{actor_type}',{before},{after},"
            f"'{summary}','{ip}','req-{uid()[:8]}',"
            f"NOW() - INTERVAL '{secs_ago} seconds') "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("")
    lines.append("COMMIT;")
    return lines


# ── Step 3: write and report ──────────────────────────────────
def main():
    print("Fetching product UUIDs from database...")
    products = fetch_products()
    if not products:
        print("ERROR: No products found. Make sure the DB is seeded first.")
        raise SystemExit(1)
    print(f"  Found {len(products)} products")

    print("Building SQL...")
    lines = build_sql(products)

    out = "scripts/seed_linked.sql"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    insert_count = sum(1 for l in lines if l.startswith("INSERT"))
    print(f"  Written {insert_count} INSERT statements to {out}")
    print("\nNow run:")
    print("  Get-Content scripts/seed_linked.sql | docker exec -i expiry_postgres psql -U expiry_user -d expiry_db")


if __name__ == "__main__":
    main()
