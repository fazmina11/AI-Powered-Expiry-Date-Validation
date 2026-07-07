
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_v2'))

from app.services.scan_pipeline_service import ScanPipelineService
from app.services.paddle_ocr_service import extract_text
from app.services.standalone_date_extractor import StandaloneDateExtractor

# Let's test with the image (we'll need to have an actual image, but let's create a placeholder)
# First, let's create a dummy image file for testing (we can use a small test image)
# Alternatively, let's test the date extraction with the text from the user's image

# The user's image has text like:
test_text = """
Description of goods: WET DATES
Produced in: I.R. of IRAN
Net Quantity: 500g
M.R.P (Inclusive of all taxes): ₹400
USP: 
Date of Packaging: 26.03.26
Use by / Batch No.: 25.09.26-K4/8
Import, Re Packed and Customer Care Executive details
JMJ EXPORTS
Address: #1, 4th Cross Street, Thirunagar,
Manachanallur, Trichy - 621 005,
Tamilnadu, India.
Customer Care No: 94875 60249, 93636 60249
Email: jmjexports19@gmail.com
Web: jmjdlite.com
Country of Origin: Iran
"""

print("Testing StandaloneDateExtractor with the test text:")
extractor = StandaloneDateExtractor()
dates = extractor.extract_dates_from_text(test_text)
print(f"Extracted dates: mfg_date={dates.mfg_date}, expiry_date={dates.expiry_date}, batch={dates.batch_number}")
