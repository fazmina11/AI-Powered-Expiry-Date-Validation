
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

if len(sys.argv) > 1:
    img_path = sys.argv[1]
else:
    img_path = 'test_dates.jpg'

print(f"Using image: {img_path}")
print(f"Checking image exists: {os.path.exists(img_path)}")

from services.paddle_ocr_service import extract_text
print("Calling extract_text...")
local_ocr = extract_text(img_path)
print("\n=== local_ocr ===")
print(f"local_ocr keys: {local_ocr.keys()}")
print(f"raw_text: {repr(local_ocr.get('raw_text', ''))}")
print(f"confidence: {local_ocr.get('confidence',0)}")
print(f"line_count: {local_ocr.get('line_count',0)}")

from services.date_extraction_service import extract_fields
print("\nCalling extract_fields...")
extracted = extract_fields(local_ocr['raw_text'] if local_ocr else '')
print("\n=== extract_fields result ===")
print(f"mfg: {extracted.candidate_mfg_date}")
print(f"exp: {extracted.candidate_expiry_date}")
print(f"batch: {extracted.candidate_batch}")
print(f"mrp: {extracted.candidate_mrp}")

from services.product_intelligence_service import ProductIntelligenceService
print("\nCalling ProductIntelligenceService.build_product_profile...")
pis = ProductIntelligenceService()
ocr_data = {
    **local_ocr,
    "expiry_date": extracted.candidate_expiry_date,
    "best_before_date": extracted.candidate_best_before or extracted.candidate_expiry_date,
    "batch_number": extracted.candidate_batch,
    "price": extracted.candidate_mrp,
    "exp_computed": extracted.exp_computed,
    "detected_fields": {
        "mfg_date": extracted.candidate_mfg_date,
        "lot_number": extracted.candidate_lot,
    }
}
print(f"ocr_data passed: {ocr_data}")

profile = pis.build_product_profile(
    barcode_data=None,
    product_lookup=None,
    ocr_data=ocr_data
)

print("\n=== profile ===")
print(f"manufacturing.manufacturing_date: {profile.manufacturing.manufacturing_date}")
print(f"expiry.expiry_date: {profile.expiry.expiry_date}")
print(f"batch.batch_number: {profile.batch.batch_number}")
print(f"ocr.raw_text: {repr(profile.ocr.raw_text)}")
