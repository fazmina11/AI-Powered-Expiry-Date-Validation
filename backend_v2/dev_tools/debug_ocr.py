"""
dev_tools/debug_ocr.py
Prints raw OCR text of the latest label image to inspect characters.
"""
from __future__ import annotations

import os
import sys

# Disable oneDNN/MKLDNN globally at process startup to bypass Windows CPU compilation bugs
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_WITH_MKLDNN"] = "0"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def main():
    # Find latest image in uploads/labels/
    labels_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "labels")
    )
    if not os.path.isdir(labels_dir):
        print("No uploads/labels/ directory found.")
        return
    files = [
        os.path.join(labels_dir, f)
        for f in os.listdir(labels_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not files:
        print("No label images found.")
        return

    latest = max(files, key=os.path.getmtime)
    print(f"Latest image: {os.path.basename(latest)}")

    from app.services.paddle_ocr_service import extract_text
    from app.services.date_extraction_service import extract_fields

    res = extract_text(latest)
    print("\n=== RAW TEXT FROM PADDLEOCR ===")
    print(res.get("raw_text", ""))
    print("===============================\n")

    fields = extract_fields(res.get("raw_text", ""))
    print("=== EXTRACTED FIELDS BY REGEX ===")
    for k, v in fields.to_dict().items():
        print(f"  {k:<24}: {v}")
    print("=================================")

if __name__ == "__main__":
    main()
