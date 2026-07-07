
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
test_img_path = 'test_dates.jpg'
print(f'Processing test image {test_img_path}...')
from services.paddle_ocr_service import extract_text
result = extract_text(test_img_path)
print(f'\n=== OCR Result ===')
print(f'Confidence: {result["confidence"]}')
print(f'Raw text:\n{repr(result["raw_text"])}')
