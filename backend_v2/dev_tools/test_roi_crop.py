"""
dev_tools/test_roi_crop.py
Visual/Standalone verification tool for testing Date ROI cropping stage.

It extracts the Date ROI from the latest label image or a specified image,
saves the preprocessed crop to `uploads/labels/roi_crop_test.jpg`, and prints
information about candidate bounding boxes detected.

Usage:
    python dev_tools/test_roi_crop.py
    python dev_tools/test_roi_crop.py uploads/labels/<some_image>.jpg
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
    # ── Resolve image ─────────────────────────────────────────
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
    print("  Sprint 5 — Standalone Date ROI Crop Tester")
    print("══════════════════════════════════════════════════════")
    print(f"Loading Image: {image_path}")

    frame = cv2.imread(image_path)
    if frame is None:
        print("[ERROR] Failed to load image using cv2.imread")
        sys.exit(1)

    # 1. Run date region candidate finder
    from app.services.date_roi_service import find_date_regions, merge_and_pad_boxes, preprocess_date_crop, extract_date_crop

    print("Running EasyOCR date keyword/pattern detection...")
    boxes = find_date_regions(frame)
    print(f"Found {len(boxes)} matching date region boxes.")

    # 2. Merge and pad
    region = merge_and_pad_boxes(boxes, frame.shape)
    if region:
        x_min, y_min, x_max, y_max = region
        print(f"Merged region coordinates: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")
        
        # Extract crop & preprocess
        crop = frame[y_min:y_max, x_min:x_max]
        processed = preprocess_date_crop(crop)

        # Write to disk
        out_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "uploads", "labels", "roi_crop_test.jpg")
        )
        cv2.imwrite(out_path, processed)
        print(f"[SUCCESS] Preprocessed ROI crop saved to: {out_path}")
        print("Please visually verify this cropped image to check if dates are isolated clearly!")
    else:
        print("[WARN] No date ROI regions detected on the label. Falling back to full image.")

    # 3. Test extract_date_crop() interface
    crop_bytes, found = extract_date_crop(frame)
    print(f"extract_date_crop() interface returns: found={found}, bytes_length={len(crop_bytes) if crop_bytes else 0}")


if __name__ == "__main__":
    main()
