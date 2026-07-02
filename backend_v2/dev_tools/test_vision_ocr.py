"""
dev_tools/test_vision_ocr.py
Sprint 5 — Vision LLM Structured Extraction Tester.
"""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

# Allow importing from backend_v2/ root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load environment variables
load_dotenv()

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
            sys.exit(1)
        print(f"[INFO] Using latest image: {os.path.basename(image_path)}\n")

    # ── Verify keys ──────────────────────────────────────────────────────────
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not gemini_key and not openai_key:
        print("[ERROR] Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured in your environment or .env file.")
        sys.exit(1)

    print("════════════════════════════════════")
    print("  Sprint 5 — Vision LLM OCR Test")
    print("════════════════════════════════════")
    print(f"  Image: {image_path}")
    print(f"  Active Keys: Gemini={'Configured' if gemini_key else 'None'}, OpenAI={'Configured' if openai_key else 'None'}\n")

    from app.services.vision_llm_service import extract_structured_fields_via_llm

    result = extract_structured_fields_via_llm(image_path)
    
    if not result:
        print("[ERROR] Vision LLM extraction returned None. Check API logs above.")
        sys.exit(1)

    # ── Print results ─────────────────────────────────────────────────────────
    print("── Structured Extraction Output ───")
    print(f"Product Name : {result.product_name}")
    print(f"MFG Date     : {result.mfg_date}")
    print(f"EXP Date     : {result.expiry_date}")
    print(f"Batch Number : {result.batch_number}")
    print(f"MRP (Price)  : {result.mrp}")
    print(f"Weight       : {result.weight}")
    print(f"Confidence   : {result.confidence_score:.4f}")
    print("───────────────────────────────────")
    print()


if __name__ == "__main__":
    main()
