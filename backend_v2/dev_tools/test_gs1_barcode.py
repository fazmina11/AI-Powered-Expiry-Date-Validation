"""
dev_tools/test_gs1_barcode.py
Sprint 5 — Standalone verification script for testing GS1 DataMatrix Direct parsing.

Loads a sample product label image containing a square 2D DataMatrix barcode,
decodes the embedded GS1 Application Identifiers, and prints out the results.

Usage:
    python dev_tools/test_gs1_barcode.py
    python dev_tools/test_gs1_barcode.py uploads/labels/<some_image>.jpg
"""

from __future__ import annotations

import os
import sys
import cv2
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()


def _latest_label_image() -> str | None:
    labels_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "labels")
    )
    if not os.path.isdir(labels_dir):
        return None
    files = [
        os.path.join(labels_dir, f)
        for f in os.listdir(labels_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png")) and "roi_crop_test" not in f
    ]
    return max(files, key=os.path.getmtime) if files else None


def main() -> None:
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = _latest_label_image()
        if not image_path:
            print("[ERROR] No image provided and no images found in uploads/labels/")
            sys.exit(1)
        print(f"[INFO] Using latest image: {os.path.basename(image_path)}\n")

    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)

    print("══════════════════════════════════════════════════════")
    print("  Sprint 5 — GS1 DataMatrix Standalone Decoder")
    print("══════════════════════════════════════════════════════")
    print(f"Loading Image: {image_path}")

    frame = cv2.imread(image_path)
    if frame is None:
        print("[ERROR] Failed to load image using cv2.imread")
        sys.exit(1)

    from app.services.gs1_barcode_service import (
        detect_and_decode_datamatrix,
        parse_gs1_string,
        extract_dates_from_datamatrix,
    )

    # 1. Detect and show raw decoded string
    print("Scanning for DataMatrix square 2D barcode...")
    raw_str = detect_and_decode_datamatrix(frame)
    if raw_str:
        print(f"[SUCCESS] Raw decoded barcode string: {repr(raw_str)}")
        
        # Parse elements
        parsed = parse_gs1_string(raw_str)
        print("\nParsed GS1 Application Identifiers:")
        for ai, val in parsed.items():
            print(f"  AI ({ai}): {val}")
    else:
        print("[INFO] No DataMatrix square barcode detected in the frame.")

    # 2. Test main extract dates interface
    res = extract_dates_from_datamatrix(frame)
    print("\nResult of extract_dates_from_datamatrix():")
    for k, v in res.items():
        print(f"  {k:<10}: {v}")


if __name__ == "__main__":
    main()
