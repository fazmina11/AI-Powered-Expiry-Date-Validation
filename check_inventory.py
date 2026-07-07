
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_v2'))

from app.database import SessionLocal
from app.models.inventory import InventoryItem

db = SessionLocal()

try:
    results = db.query(InventoryItem).order_by(InventoryItem.created_at.desc()).limit(10).all()
    print(f"Found {len(results)} inventory items:")
    for r in results:
        print(f"\nID: {r.id}")
        print(f"Product ID: {r.product_id}")
        print(f"Batch: {r.batch_number}")
        print(f"Mfg date: {r.manufacturing_date}")
        print(f"Exp date: {r.expiry_date}")
        print(f"Status: {r.intake_status}")
finally:
    db.close()
