"""
dev_tools/test_combination_pipeline.py
Sprint 5 — End-to-end combined OCR + LLM pipeline tester.

This script runs the full 3-stage pipeline on a single image and reports
what each stage found, along with the final merged result.

Usage:
    python dev_tools/test_combination_pipeline.py <image_path>
    python dev_tools/test_combination_pipeline.py  # uses latest in uploads/labels/
"""

from __future__ import annotations

import os
import sys
import time
from dotenv import load_dotenv

# Allow importing from backend_v2/ root
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
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    return max(files, key=os.path.getmtime) if files else None


def _divider(title: str) -> None:
    width = 54
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


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

    print("╔══════════════════════════════════════════════════════╗")
    print("║  Sprint 5 — Combined OCR + LLM Combination Pipeline  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"Image : {image_path}")
    print(f"Gemini: {'✓ Configured' if os.environ.get('GEMINI_API_KEY') else '✗ Not set'}")
    print(f"OpenAI: {'✓ Configured' if os.environ.get('OPENAI_API_KEY') else '✗ Not set'}")

    # ─────────────────────────────────────────────────────────
    # STAGE 4A: Local PaddleOCR
    # ─────────────────────────────────────────────────────────
    _divider("Stage 4A: Local PaddleOCR")
    local_ocr = None
    t0 = time.time()
    try:
        from app.services.paddle_ocr_service import extract_text
        local_ocr = extract_text(image_path)
        elapsed = time.time() - t0
        print(f"  Lines     : {local_ocr.get('line_count', 0)}")
        print(f"  Confidence: {local_ocr.get('confidence', 0):.4f}")
        print(f"  Time      : {elapsed:.2f}s")
        print(f"\n  Raw Text Preview:")
        preview = (local_ocr.get("raw_text") or "")[:300]
        for line in preview.split("\n"):
            print(f"    {line}")
    except Exception as exc:
        print(f"  [FAILED] {exc}")

    # ─────────────────────────────────────────────────────────
    # STAGE 4B: Text LLM (OCR text → structured JSON)
    # ─────────────────────────────────────────────────────────
    _divider("Stage 4B: Text LLM Parser (OCR Text → Structured JSON)")
    llm_text_result = None
    if local_ocr and local_ocr.get("raw_text"):
        t0 = time.time()
        try:
            from app.services.vision_llm_service import extract_structured_fields_from_text
            llm_text_result = extract_structured_fields_from_text(local_ocr["raw_text"])
            elapsed = time.time() - t0
            if llm_text_result:
                print(f"  Product   : {llm_text_result.product_name}")
                print(f"  MFG Date  : {llm_text_result.mfg_date}")
                print(f"  EXP Date  : {llm_text_result.expiry_date}")
                print(f"  Batch     : {llm_text_result.batch_number}")
                print(f"  MRP       : {llm_text_result.mrp}")
                print(f"  Weight    : {llm_text_result.weight}")
                print(f"  Confidence: {llm_text_result.confidence_score:.4f}")
                print(f"  Time      : {elapsed:.2f}s")
            else:
                print("  [SKIPPED] No API key configured or LLM returned None.")
        except Exception as exc:
            print(f"  [FAILED] {exc}")
    else:
        print("  [SKIPPED] No raw text from PaddleOCR to parse.")

    # ─────────────────────────────────────────────────────────
    # STAGE 4C: Vision LLM (raw image → structured JSON)
    #   — only runs if Stage 4B found no dates
    # ─────────────────────────────────────────────────────────
    dates_missing = (
        llm_text_result is None
        or (not llm_text_result.expiry_date and not llm_text_result.mfg_date)
    )
    llm_vision_result = None
    _divider("Stage 4C: Vision LLM (Raw Image → Structured JSON)")
    if dates_missing:
        t0 = time.time()
        try:
            from app.services.vision_llm_service import extract_structured_fields_via_llm
            llm_vision_result = extract_structured_fields_via_llm(image_path)
            elapsed = time.time() - t0
            if llm_vision_result:
                print(f"  Product   : {llm_vision_result.product_name}")
                print(f"  MFG Date  : {llm_vision_result.mfg_date}")
                print(f"  EXP Date  : {llm_vision_result.expiry_date}")
                print(f"  Batch     : {llm_vision_result.batch_number}")
                print(f"  MRP       : {llm_vision_result.mrp}")
                print(f"  Weight    : {llm_vision_result.weight}")
                print(f"  Confidence: {llm_vision_result.confidence_score:.4f}")
                print(f"  Time      : {elapsed:.2f}s")
            else:
                print("  [SKIPPED] No API key configured or Vision LLM returned None.")
        except Exception as exc:
            print(f"  [FAILED] {exc}")
    else:
        print("  [SKIPPED] Stage 4B returned valid dates — Vision LLM not needed.")

    # ─────────────────────────────────────────────────────────
    # Final Merged Result
    # ─────────────────────────────────────────────────────────
    final = llm_vision_result or llm_text_result
    _divider("✅ Final Merged Extraction Result")
    if final:
        print(f"  Source    : {'Vision LLM' if llm_vision_result else 'Text LLM'}")
        print(f"  MFG Date  : {final.mfg_date or '—'}")
        print(f"  EXP Date  : {final.expiry_date or '—'}")
        print(f"  Batch     : {final.batch_number or '—'}")
        print(f"  MRP       : {final.mrp or '—'}")
        print(f"  Weight    : {final.weight or '—'}")
        print(f"  Confidence: {final.confidence_score:.4f}")
    else:
        print("  [WARN] No structured result from any LLM stage.")
        print("         Regex heuristics would run in the live pipeline.")
    print()


if __name__ == "__main__":
    main()
