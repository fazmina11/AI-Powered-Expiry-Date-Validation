"""
dev_tools/test_ocr.py
Sprint 3 — Standalone OCR extraction tester.

Usage:
    # Test a specific saved label image
    ../venv/bin/python dev_tools/test_ocr.py uploads/labels/20260625_041500_000000.jpg

    # Auto-pick the most recent image in uploads/labels/
    ../venv/bin/python dev_tools/test_ocr.py

    # Pipe any image path
    ../venv/bin/python dev_tools/test_ocr.py /path/to/any/image.jpg

Output example:
    ════════════════════════════════════
     Sprint 3 — OCR Extraction Test
    ════════════════════════════════════
    Image      : uploads/labels/20260625_...jpg
    Lines found: 4
    Confidence : 0.9312

    ── Raw Text ─────────────────────────
    MFG DATE 01/05/2026
    BEST BEFORE 01/11/2026
    BATCH NO A1234
    NET WT 500g
    ─────────────────────────────────────

This file is a standalone dev tool.
NO FastAPI. NO database. NO date parsing.
"""

from __future__ import annotations

import os
import sys

# Allow importing from backend_v2/ root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _latest_label_image() -> str | None:
    """Return the most recently saved file in uploads/labels/, or None."""
    labels_dir = os.path.join(
        os.path.dirname(__file__), "..", "uploads", "labels"
    )
    labels_dir = os.path.abspath(labels_dir)

    if not os.path.isdir(labels_dir):
        return None

    files = [
        os.path.join(labels_dir, f)
        for f in os.listdir(labels_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not files:
        return None

    return max(files, key=os.path.getmtime)


def main() -> None:
    # ── Resolve image path ────────────────────────────────────────────────────
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = _latest_label_image()
        if not image_path:
            print("[ERROR] No image path provided and no images found in uploads/labels/")
            print()
            print("Usage:")
            print("  ../venv/bin/python dev_tools/test_ocr.py <image_path>")
            print()
            print("Capture a label first using camera_test.py (press SPACE).")
            sys.exit(1)
        print(f"[INFO] No path given — using latest: {os.path.basename(image_path)}\n")

    # ── Import OCR service (heavy — loads PaddleOCR model on first call) ──────
    try:
        from app.services.paddle_ocr_service import extract_text
    except ImportError as exc:
        print(f"[ERROR] Could not import paddle_ocr_service: {exc}")
        print("  Run: pip install paddleocr paddlepaddle")
        sys.exit(1)

    # ── Run extraction ────────────────────────────────────────────────────────
    print("════════════════════════════════════")
    print("  Sprint 3 — OCR Extraction Test")
    print("════════════════════════════════════")
    print(f"  Image: {image_path}")
    print("  Loading PaddleOCR model (first run may download weights)...\n")

    try:
        result = extract_text(image_path)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] OCR failed: {exc}")
        sys.exit(1)

    # ── Print results ─────────────────────────────────────────────────────────
    print(f"Image      : {result['image_path']}")
    print(f"Lines found: {result['line_count']}")
    print(f"Confidence : {result['confidence']:.4f}")
    print()
    print("── Raw Text " + "─" * 30)

    if result["raw_text"]:
        print(result["raw_text"])
    else:
        print("(no text detected)")

    print("─" * 41)
    print()


if __name__ == "__main__":
    main()
