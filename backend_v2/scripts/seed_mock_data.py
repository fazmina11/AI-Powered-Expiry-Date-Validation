"""
scripts/seed_mock_data.py
=========================
Seeds ALL 9 tables with realistic linked mock data.

Tables covered:
  1. products          — 20 retail products
  2. barcode_scans     — 25 scan events (resolved + unresolved)
  3. inventory_items   — 25 warehouse intake batches
  4. product_images    — 30 label/photo uploads
  5. ocr_results       — 28 OCR extraction records
  6. storage_contexts  — 25 storage location records
  7. ml_predictions    — 20 ML prediction records
  8. manual_reviews    — 10 human review records
  9. audit_logs        — 40 event log entries

Idempotent: running multiple times will not create duplicates.
All foreign keys are wired correctly across all tables.

Usage:
    python scripts/seed_mock_data.py
"""

import os, sys, uuid, random
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# ── Connection ────────────────────────────────────────────────
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://expiry_user:expiry_pass@127.0.0.1:5432/expiry_db"
)

def get_conn():
    return psycopg2.connect(DB_URL)

def uid():
    return str(uuid.uuid4())

def now():
    return datetime.now(timezone.utc)

def days_ago(n):
    return (datetime.now(timezone.utc) - timedelta(days=n)).date()

def days_from_now(n):
    return (date.today() + timedelta(days=n))

# ── 1. PRODUCTS (20) ─────────────────────────────────────────
PRODUCTS = [
    ("Amul Taaza Milk 500ml",          "Amul",          "AMUL-TAAZA-500ML",     "8901262010011", "EAN13", "Dairy",          "Pasteurised toned milk pouch.",                    "refrigerated"),
    ("Nestle Everyday Whitener 400g",  "Nestle",        "NESTLE-EW-400G",       "8901058850123", "EAN13", "Dairy",          "Dairy whitener powder for tea and coffee.",         "ambient"),
    ("Mother Dairy Classic Curd 400g", "Mother Dairy",  "MD-CURD-400G",         "8901648004321", "EAN13", "Dairy",          "Fresh curd requiring cold storage.",                "refrigerated"),
    ("Amul Salted Butter 100g",        "Amul",          "AMUL-BUTTER-100G",     "8901262030019", "EAN13", "Dairy",          "Salted butter block, 100g.",                        "refrigerated"),
    ("Britannia Good Day Cookies 200g","Britannia",     "BRIT-GD-200G",         "8901063160012", "EAN13", "Snacks",         "Cashew cookies packed for retail.",                 "ambient"),
    ("Parle-G Glucose Biscuits 250g",  "Parle",         "PARLE-G-250G",         "8901719101015", "EAN13", "Snacks",         "Classic glucose biscuits.",                         "ambient"),
    ("Lay's Classic Salted Chips 52g", "Lay's",         "LAYS-CLASSIC-52G",     "8901491100226", "EAN13", "Snacks",         "Classic salted potato chips.",                      "ambient"),
    ("Kurkure Masala Munch 90g",       "Kurkure",       "KURKURE-MASALA-90G",   "8901491501221", "EAN13", "Snacks",         "Spicy crunchy corn snack.",                         "ambient"),
    ("Coca-Cola Original 750ml",       "Coca-Cola",     "COKE-750ML",           "8901764012342", "EAN13", "Beverages",      "Carbonated soft drink bottle.",                     "ambient"),
    ("Real Mixed Fruit Juice 1L",      "Real",          "REAL-MIXED-1L",        "8901207011123", "EAN13", "Beverages",      "Packaged mixed fruit juice carton.",                "ambient"),
    ("Tropicana Orange Delight 1L",    "Tropicana",     "TROP-ORANGE-1L",       "8901491200452", "EAN13", "Beverages",      "Packaged orange fruit beverage.",                   "ambient"),
    ("Bisleri Mineral Water 1L",       "Bisleri",       "BISLERI-1L",           "8901207040017", "EAN13", "Beverages",      "Packaged drinking water, 1-litre.",                 "ambient"),
    ("Harvest Gold White Bread 400g",  "Harvest Gold",  "HG-WHITE-BREAD-400G",  "8901725180089", "EAN13", "Bakery",         "Packaged white bread loaf.",                        "ambient"),
    ("Britannia Brown Bread 400g",     "Britannia",     "BRIT-BROWN-BREAD-400G","8901063019870", "EAN13", "Bakery",         "Packaged brown bread loaf.",                        "ambient"),
    ("Maggi Masala Noodles 70g",       "Maggi",         "MAGGI-MASALA-70G",     "8901058840018", "EAN13", "Packaged Foods", "Instant noodles with masala tastemaker.",           "ambient"),
    ("Aashirvaad Whole Wheat Atta 1kg","Aashirvaad",    "AASHIRVAAD-ATTA-1KG",  "8901725123456", "EAN13", "Packaged Foods", "Whole wheat flour pack.",                           "ambient"),
    ("Tata Salt Iodized 1kg",          "Tata",          "TATA-SALT-1KG",        "8904043901017", "EAN13", "Packaged Foods", "Iodized salt packet.",                              "ambient"),
    ("Fortune Sunflower Oil 1L",       "Fortune",       "FORTUNE-SFO-1L",       "8906007280012", "EAN13", "Packaged Foods", "Refined sunflower cooking oil.",                    "ambient"),
    ("Dove Cream Beauty Bar 100g",     "Dove",          "DOVE-BAR-100G",        "8901030865432", "EAN13", "Personal Care",  "Moisturizing bathing soap bar.",                    "ambient"),
    ("Dettol Antiseptic Liquid 250ml", "Dettol",        "DETTOL-250ML",         "8901396389012", "EAN13", "Personal Care",  "Antiseptic disinfectant liquid.",                   "ambient"),
]


def seed_products(cur):
    """Insert 20 products. Returns list of (id, barcode, category, default_storage_type)."""
    ids = []
    inserted = skipped = 0
    for (name, brand, sku, barcode, btype, cat, desc, storage) in PRODUCTS:
        cur.execute("SELECT id FROM products WHERE barcode=%s OR sku=%s", (barcode, sku))
        row = cur.fetchone()
        if row:
            ids.append((str(row["id"]), barcode, cat, storage))
            skipped += 1
            continue
        pid = uid()
        cur.execute("""
            INSERT INTO products
              (id, name, brand, sku, barcode, barcode_type, category,
               description, default_storage_type, is_active, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE,NOW(),NOW())
        """, (pid, name, brand, sku, barcode, btype, cat, desc, storage))
        ids.append((pid, barcode, cat, storage))
        inserted += 1
    print(f"  products        inserted={inserted}  skipped={skipped}")
    return ids


def seed_barcode_scans(cur, products):
    """25 scan events: 20 resolved (one per product) + 5 unresolved."""
    scan_ids = []
    for pid, barcode, _, _ in products:
        sid = uid()
        cur.execute("""
            INSERT INTO barcode_scans
              (id, product_id, raw_barcode, barcode_type, scan_source,
               scan_status, scanned_at, created_at)
            VALUES (%s,%s,%s,'EAN13','handheld_scanner','resolved',NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (sid, pid, barcode))
        scan_ids.append((sid, pid))

    # 5 unresolved scans (unknown barcodes)
    unknown = ["9990000000001","9990000000002","9990000000003","9990000000004","9990000000005"]
    for bc in unknown:
        sid = uid()
        cur.execute("""
            INSERT INTO barcode_scans
              (id, product_id, raw_barcode, barcode_type, scan_source,
               scan_status, notes, scanned_at, created_at)
            VALUES (%s,NULL,%s,'EAN13','mobile_app','unresolved',
                    'Barcode not found in product catalogue',NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (sid, bc))

    print(f"  barcode_scans   inserted={len(scan_ids)+5}")
    return scan_ids


def seed_inventory_items(cur, products, scan_ids):
    """25 inventory intake batches — one per product + 5 extras with varied statuses."""
    inv_ids = []
    statuses = ["PENDING_OCR","OCR_COMPLETED","PENDING_ML_REVIEW","ML_COMPLETED","MANUAL_REVIEW"]

    for i, ((pid, barcode, cat, storage), (sid, _)) in enumerate(zip(products, scan_ids)):
        iid = uid()
        mfg = days_ago(random.randint(30, 180))
        # Vary expiry: some good, some near, some expired
        if i % 5 == 0:
            exp = days_from_now(-5)      # EXPIRED
        elif i % 5 == 1:
            exp = days_from_now(15)      # near expiry
        elif i % 5 == 2:
            exp = days_from_now(45)      # priority sale range
        elif i % 5 == 3:
            exp = days_from_now(120)     # good
        else:
            exp = None                   # missing — manual review

        pipeline = statuses[i % len(statuses)]
        batch = f"BATCH-{2026001 + i}"

        cur.execute("""
            INSERT INTO inventory_items
              (id, product_id, barcode_scan_id, batch_number,
               manufacturing_date, expiry_date, pipeline_status,
               quantity, unit, intake_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'units',NOW(),NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (iid, pid, sid, batch, mfg, exp, pipeline, random.randint(1, 50)))
        inv_ids.append((iid, pid, exp, pipeline, storage))

    print(f"  inventory_items inserted={len(inv_ids)}")
    return inv_ids


def seed_product_images(cur, products):
    """30 image uploads — at least one per product, some have two."""
    img_ids = []
    types = ["front_label","back_label","barcode_close_up","product_photo"]
    statuses = ["uploaded","ocr_pending","ocr_completed","failed"]

    for i, (pid, barcode, cat, _) in enumerate(products):
        # Every product gets one image
        iid = uid()
        cur.execute("""
            INSERT INTO product_images
              (id, product_id, file_path, file_url, file_size_bytes,
               mime_type, image_type, processing_status,
               uploaded_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,'image/jpeg',%s,%s,NOW(),NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (
            iid, pid,
            f"/uploads/products/{barcode}_label_{i}.jpg",
            f"https://cdn.expiry.local/products/{barcode}_label_{i}.jpg",
            random.randint(80000, 500000),
            types[i % len(types)],
            statuses[i % len(statuses)]
        ))
        img_ids.append((iid, pid))

        # First 10 products get a second image
        if i < 10:
            iid2 = uid()
            cur.execute("""
                INSERT INTO product_images
                  (id, product_id, file_path, file_url, file_size_bytes,
                   mime_type, image_type, processing_status,
                   uploaded_at, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,'image/jpeg','barcode_close_up','uploaded',
                        NOW(),NOW(),NOW())
                ON CONFLICT DO NOTHING
            """, (
                iid2, pid,
                f"/uploads/products/{barcode}_barcode_{i}.jpg",
                f"https://cdn.expiry.local/products/{barcode}_barcode_{i}.jpg",
                random.randint(30000, 100000),
            ))
            img_ids.append((iid2, pid))

    print(f"  product_images  inserted={len(img_ids)}")
    return img_ids


def seed_ocr_results(cur, img_ids, inv_ids):
    """28 OCR results linked to product images and inventory items."""
    ocr_ids = []
    engines = ["tesseract-5.3","google-vision-v1","aws-textract-v2"]
    statuses = ["pending","completed","completed","completed","failed"]
    raw_texts = [
        "MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A",
        "Manufacturing Date: March 2026  Best Before: Sep 2026",
        "Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421",
        "MFG 2026-01-10  EXP 2026-07-10  LOT 9921B",
        "PROD DATE: 20/04/26  EXP DATE: 20/10/26",
        "Label torn — partial text only: ...exp 06/2026...",
        "MFG: Feb 2026  EXP: Aug 2026",
    ]
    blocks_examples = [
        [{"label": "MFG", "value": "01/03/2026"}, {"label": "EXP", "value": "01/09/2026"}],
        [{"label": "Best Before", "value": "Sep 2026"}],
        [{"label": "Mfd", "value": "15.02.2026"}, {"label": "Use by", "value": "15.08.2026"}],
        [],
    ]

    for i, (img_id, pid) in enumerate(img_ids[:28]):
        oid = uid()
        inv_id = inv_ids[i % len(inv_ids)][0] if inv_ids else None
        status = statuses[i % len(statuses)]
        confidence = round(random.uniform(0.55, 0.99), 4) if status == "completed" else None
        cur.execute("""
            INSERT INTO ocr_results
              (id, product_image_id, inventory_item_id, raw_text, ocr_engine,
               ocr_engine_version, extracted_text_blocks, overall_confidence,
               ocr_status, failure_reason, processed_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,'1.0',%s,%s,%s,%s,
                    CASE WHEN %s='completed' THEN NOW() ELSE NULL END,
                    NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (
            oid, img_id, inv_id,
            raw_texts[i % len(raw_texts)],
            engines[i % len(engines)],
            json.dumps(blocks_examples[i % len(blocks_examples)]),
            confidence,
            status,
            "OCR engine timeout" if status == "failed" else None,
            status,
        ))
        ocr_ids.append(oid)

    print(f"  ocr_results     inserted={len(ocr_ids)}")
    return ocr_ids


def seed_storage_contexts(cur, inv_ids):
    """One storage context per inventory item (25 records)."""
    zones   = ["Zone-A","Zone-B","Cold-Room-1","Cold-Room-2","Frozen-Bay","Ambient-Rack-3"]
    s_types = ["ambient","refrigerated","frozen","controlled"]
    wh_ids  = ["WH-DELHI-01","WH-MUMBAI-02","WH-BANGALORE-03"]

    for i, (inv_id, pid, exp, pipeline, storage) in enumerate(inv_ids):
        s_type = "refrigerated" if storage == "refrigerated" else \
                 "frozen"       if storage == "frozen"       else "ambient"
        temp = round(random.uniform(2.0, 8.0), 2)  if s_type == "refrigerated" else \
               round(random.uniform(-20.0, -15.0), 2) if s_type == "frozen"    else \
               round(random.uniform(18.0, 28.0), 2)
        humid = round(random.uniform(40.0, 70.0), 2)

        cur.execute("""
            INSERT INTO storage_contexts
              (id, inventory_item_id, warehouse_id, zone, aisle, shelf,
               bin_location, storage_type, temperature_celsius, humidity_percent,
               notes, recorded_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),NOW())
            ON CONFLICT (inventory_item_id) DO NOTHING
        """, (
            uid(), inv_id,
            wh_ids[i % len(wh_ids)],
            zones[i % len(zones)],
            f"A{(i % 5) + 1}",
            f"S{(i % 4) + 1}",
            f"BIN-{100 + i}",
            s_type, temp, humid,
            f"Auto-recorded on intake. Storage: {s_type}.",
        ))

    print(f"  storage_contexts inserted={len(inv_ids)}")


def seed_ml_predictions(cur, inv_ids):
    """20 ML predictions for the first 20 inventory items."""
    decisions  = ["ACCEPTED","PRIORITY_SALE","REJECTED","REJECTED","REQUIRES_REVIEW"]
    reasons    = [
        "Product has sufficient shelf life remaining.",
        "Nearing expiry — prioritize for immediate sale.",
        "Product is already expired. Do not sell.",
        "Remaining shelf life below minimum threshold.",
        "Confidence too low — requires human review.",
    ]

    for i, (inv_id, pid, exp, pipeline, _) in enumerate(inv_ids[:20]):
        decision = decisions[i % len(decisions)]
        remaining = (exp - date.today()).days if exp else None
        confidence = round(random.uniform(0.72, 0.99), 4)

        cur.execute("""
            INSERT INTO ml_predictions
              (id, inventory_item_id, model_name, model_version,
               predicted_expiry_date, predicted_remaining_days,
               predicted_decision, decision_confidence, decision_reason,
               prediction_status, predicted_at, created_at, updated_at)
            VALUES (%s,%s,'expiry-shelf-v2.1','2.1.0',%s,%s,%s,%s,%s,
                    'completed',NOW(),NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (
            uid(), inv_id, exp, remaining,
            decision, confidence, reasons[i % len(reasons)],
        ))

    print(f"  ml_predictions  inserted=20")


def seed_manual_reviews(cur, inv_ids):
    """10 manual review records for items that need human attention."""
    roles       = ["warehouse_staff","supervisor","qa"]
    decisions   = ["ACCEPTED","REJECTED","PRIORITY_SALE","ESCALATE_TO_QA"]
    escalations = [
        "OCR failed — label was torn.",
        "ML confidence 0.43 — below threshold.",
        "Conflicting dates found on packaging.",
        "Product close to expiry — supervisor review required.",
        "Batch number missing from label.",
    ]

    for i, (inv_id, pid, exp, pipeline, _) in enumerate(inv_ids[:10]):
        corrected_exp = (exp + timedelta(days=2)) if exp else days_from_now(30)
        cur.execute("""
            INSERT INTO manual_reviews
              (id, inventory_item_id, reviewer_id, reviewer_role,
               corrected_expiry_date, human_decision, review_notes,
               escalation_reason, review_status, reviewed_at,
               created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,
                    CASE WHEN %s < 5 THEN 'completed' ELSE 'pending' END,
                    CASE WHEN %s < 5 THEN NOW() ELSE NULL END,
                    NOW(),NOW())
            ON CONFLICT DO NOTHING
        """, (
            uid(), inv_id,
            f"USR-{1000 + i}",
            roles[i % len(roles)],
            corrected_exp,
            decisions[i % len(decisions)],
            f"Manually verified batch. Corrected expiry date confirmed.",
            escalations[i % len(escalations)],
            i, i,
        ))

    print(f"  manual_reviews  inserted=10")


def seed_audit_logs(cur, products, inv_ids, ocr_ids):
    """40 audit log entries covering all major event types."""
    events = [
        # (event_type, entity_type, actor_type, summary_template)
        ("product.created",             "product",        "system",    "Product registered in catalogue."),
        ("inventory.intake",            "inventory_item", "service",   "Batch received at warehouse intake."),
        ("ocr.completed",               "ocr_result",     "service",   "OCR extraction completed successfully."),
        ("ocr.failed",                  "ocr_result",     "service",   "OCR extraction failed — engine timeout."),
        ("ml.prediction_received",      "inventory_item", "ml_team",   "ML prediction returned with decision."),
        ("manual_review.completed",     "inventory_item", "user",      "Manual review completed by warehouse staff."),
        ("status.changed",              "inventory_item", "system",    "Pipeline status updated."),
        ("barcode.scanned",             "barcode_scan",   "service",   "Barcode scanned via handheld scanner."),
        ("product.updated",             "product",        "user",      "Product details updated."),
        ("inventory.flagged_for_review","inventory_item", "system",    "Item flagged for manual review."),
    ]

    count = 0
    for i in range(40):
        event_type, entity_type, actor_type, summary = events[i % len(events)]

        # Pick a realistic entity_id based on event type
        if entity_type == "product" and products:
            entity_id = products[i % len(products)][0]
        elif entity_type == "inventory_item" and inv_ids:
            entity_id = inv_ids[i % len(inv_ids)][0]
        elif entity_type == "ocr_result" and ocr_ids:
            entity_id = ocr_ids[i % len(ocr_ids)]
        else:
            entity_id = str(uuid.uuid4())

        before = json.dumps({"status": "PENDING_OCR"})   if "status" in summary.lower() else None
        after  = json.dumps({"status": "OCR_COMPLETED"}) if "status" in summary.lower() else None

        cur.execute("""
            INSERT INTO audit_logs
              (id, event_type, entity_type, entity_id,
               actor_id, actor_type,
               before_state, after_state, change_summary,
               ip_address, request_id, occurred_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    NOW() - INTERVAL '%s seconds')
        """, (
            uid(), event_type, entity_type, entity_id,
            f"actor-{1000 + (i % 10)}", actor_type,
            before, after, summary,
            f"10.0.{(i % 4) + 1}.{(i % 20) + 1}",
            f"req-{uid()[:8]}",
            i * 120,   # spread events ~2 minutes apart going backwards
        ))
        count += 1

    print(f"  audit_logs      inserted={count}")


# ── MAIN ─────────────────────────────────────────────────────
def main():
    print("\nConnecting to PostgreSQL...")
    try:
        conn = get_conn()
    except Exception as e:
        print(f"ERROR: Cannot connect — {e}")
        print("Make sure Docker is running:  docker-compose up -d")
        sys.exit(1)

    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        print("\nSeeding all tables...\n")

        product_rows = seed_products(cur)
        conn.commit()

        scan_ids = seed_barcode_scans(cur, product_rows)
        conn.commit()

        inv_ids = seed_inventory_items(cur, product_rows, scan_ids)
        conn.commit()

        img_ids = seed_product_images(cur, product_rows)
        conn.commit()

        ocr_ids = seed_ocr_results(cur, img_ids, inv_ids)
        conn.commit()

        seed_storage_contexts(cur, inv_ids)
        conn.commit()

        seed_ml_predictions(cur, inv_ids)
        conn.commit()

        seed_manual_reviews(cur, inv_ids)
        conn.commit()

        seed_audit_logs(cur, product_rows, inv_ids, ocr_ids)
        conn.commit()

        # ── Final counts ──────────────────────────────────────
        print("\n" + "─" * 52)
        print("  VERIFICATION — Row counts in each table")
        print("─" * 52)
        for table in [
            "products", "barcode_scans", "inventory_items",
            "product_images", "ocr_results", "storage_contexts",
            "ml_predictions", "manual_reviews", "audit_logs"
        ]:
            cur.execute(f"SELECT COUNT(*) AS n FROM {table}")
            n = cur.fetchone()["n"]
            print(f"  {table:<22} {n:>4} rows")
        print("─" * 52)
        print("\n✅ All tables seeded successfully.\n")
        print("View in pgAdmin:  http://localhost:5050")
        print("  Email:    admin@expiryvalidation.com")
        print("  Password: admin123\n")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
