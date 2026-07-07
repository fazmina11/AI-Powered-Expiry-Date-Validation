
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
from services.date_extraction_service import extract_fields

raw_text = "Happilo Dates\n05/03/24\n04/03/26\nBatch HD1234 MRP:299"
print("Testing raw text with no prefixes:")
print(f"raw_text:", repr(raw_text))
result = extract_fields(raw_text)
print("result.candidate_mfg_date:", result.candidate_mfg_date)
print("result.candidate_expiry_date:", result.candidate_expiry_date)
print("result.batch:", result.candidate_batch)
print("result.mrp:", result.candidate_mrp)
print("all_dates_found:", result.all_dates_found)
