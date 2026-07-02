import os
import sys
from datetime import date

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.standalone_date_extractor import StandaloneDateExtractor
from app.services.barcode_intelligence_service import BarcodeIntelligenceService
from app.services.product_intelligence_service import ProductIntelligenceService
from app.schemas.product_intelligence_schema import ProductIntelligence

def test_requests():
    print("=== Testing Request 1: Date parsing & subtraction math ===")
    raw_ocr = "MFG: 2026-01-10 EXP: 2026-07-10 BATCH: LOT999 INGREDIENTS: Sugar, Cocoa, Milk, Vanilla"
    extracted = StandaloneDateExtractor.extract_dates_from_text(raw_ocr)
    
    print(f"Raw text: {raw_ocr}")
    print(f"Extracted MFG: {extracted.mfg_date} (type: {type(extracted.mfg_date)})")
    print(f"Extracted EXP: {extracted.expiry_date} (type: {type(extracted.expiry_date)})")
    print(f"Extracted Ingredients: {extracted.ingredients}")
    
    # Assert ingredients extraction (OCR normalizes to uppercase)
    assert "SUGAR, COCOA, MILK, VANILLA" in extracted.ingredients.upper(), "Ingredients extraction failed"
    
    # Build intelligence profile
    intel_service = ProductIntelligenceService()
    
    # Setup dummy barcode intelligence for supplier grade testing (Request 3)
    # Prefix "8901" is in our lookup map (mapped to A)
    barcode_intel = BarcodeIntelligenceService().parse_barcode("8901058850817")
    
    print("\n=== Testing Request 3: Supplier Grade Lookup ===")
    print(f"Barcode: {barcode_intel.value}")
    print(f"Manufacturer Code: {barcode_intel.manufacturer_code}")
    
    # Process intelligence
    intel = intel_service.build_product_profile(
        barcode_data=barcode_intel,
        ocr_data={
            "mfg_date": extracted.mfg_date,
            "expiry_date": extracted.expiry_date,
            "batch_number": extracted.batch_number,
            "ingredients": extracted.ingredients,
            "category": "Chocolate",
            "confidence": 0.95
        }
    )
    
    print(f"Supplier Grade in Profile: {intel.barcode.supplier_grade}")
    assert intel.barcode.supplier_grade == "A", f"Expected supplier grade A, got {intel.barcode.supplier_grade}"
    
    print("\n=== Testing Request 2: Category and Date field type assertions ===")
    print(f"Category in Profile: {intel.product.category}")
    assert intel.product.category == "Chocolate", "Category mapping failed"
    
    # Verify date math on proper Date objects (Request 1)
    mfg_date = intel.manufacturing.manufacturing_date
    exp_date = intel.expiry.expiry_date
    
    print(f"Profile manufacturing_date type: {type(mfg_date)}")
    print(f"Profile expiry_date type: {type(exp_date)}")
    
    assert isinstance(mfg_date, date), "manufacturing_date is not a proper date object"
    assert isinstance(exp_date, date), "expiry_date is not a proper date object"
    
    # Perform math
    printed_shelf_life = (exp_date - mfg_date).days
    days_since_mfg = (date.today() - mfg_date).days
    
    print(f"Printed Shelf Life: {printed_shelf_life} days")
    print(f"Days since manufacture: {days_since_mfg} days")
    
    assert printed_shelf_life == 181, f"Expected 181 days, got {printed_shelf_life}"
    
    print("\nALL REQUEST ASSERTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_requests()
