import os
import sys
import uuid
from datetime import datetime, timedelta

# Add the project root to the python path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.scan_alert import ScanAlert
from app.models.manual_review import ManualReview
from app.models.inventory import InventoryItem
from app.models.product import Product

def seed_data():
    db = SessionLocal()
    
    print("Clearing old alerts and reviews...")
    db.query(ScanAlert).delete()
    db.query(ManualReview).delete()
    db.commit()
    
    print("Fetching existing inventory items...")
    inventory_items = db.query(InventoryItem).limit(10).all()
    
    if not inventory_items:
        print("No inventory items found! Please add some inventory first.")
        return
        
    print(f"Found {len(inventory_items)} inventory items to attach alerts to.")
    
    # Create some dummy alerts
    alert_types = [
        ("OCR_FAILED", "CRITICAL", "Could not read OCR text clearly"),
        ("MISSING_EXPIRY", "WARNING", "Expiry date not found on package"),
        ("UNKNOWN_BARCODE", "CRITICAL", "Barcode 890123456789 not found in database"),
        ("LOW_CONFIDENCE", "WARNING", "OCR confidence for expiry date is below 80%"),
        ("INVALID_BATCH", "WARNING", "Batch number format looks unusual")
    ]
    
    now = datetime.now()
    alerts = []
    
    # Unresolved alerts
    for i, inv in enumerate(inventory_items[:5]):
        atype, severity, msg = alert_types[i % len(alert_types)]
        alert = ScanAlert(
            inventory_item_id=inv.id,
            alert_type=atype,
            severity=severity,
            message=msg,
            is_resolved=False,
            created_at=now - timedelta(days=i)
        )
        alerts.append(alert)
        
    # Resolved alerts
    for i, inv in enumerate(inventory_items[5:8]):
        atype, severity, msg = alert_types[i % len(alert_types)]
        alert = ScanAlert(
            inventory_item_id=inv.id,
            alert_type=atype,
            severity=severity,
            message=msg,
            is_resolved=True,
            resolved_at=now - timedelta(hours=i),
            resolved_by="admin",
            created_at=now - timedelta(days=i+2)
        )
        alerts.append(alert)
        
    db.add_all(alerts)
    
    # Create some dummy manual reviews
    reviews = []
    
    # Pending reviews
    for i, inv in enumerate(inventory_items[:4]):
        review = ManualReview(
            inventory_item_id=inv.id,
            review_type="OCR_CORRECTION",
            original_mfg_date=now.date() - timedelta(days=30),
            original_expiry_date=now.date() + timedelta(days=30),
            review_status="PENDING",
            created_at=now - timedelta(hours=i*2)
        )
        reviews.append(review)
        
    # Resolved reviews
    for i, inv in enumerate(inventory_items[4:6]):
        review = ManualReview(
            inventory_item_id=inv.id,
            review_type="OCR_CORRECTION",
            original_mfg_date=now.date() - timedelta(days=30),
            original_expiry_date=now.date() + timedelta(days=30),
            corrected_mfg_date=now.date() - timedelta(days=29),
            human_decision="APPROVE",
            review_status="RESOLVED",
            reviewed_at=now - timedelta(hours=1),
            reviewer_name="System Admin",
            created_at=now - timedelta(days=1)
        )
        reviews.append(review)
        
    db.add_all(reviews)
    db.commit()
    
    print(f"Successfully seeded {len(alerts)} alerts and {len(reviews)} manual reviews!")
    db.close()

if __name__ == "__main__":
    seed_data()
