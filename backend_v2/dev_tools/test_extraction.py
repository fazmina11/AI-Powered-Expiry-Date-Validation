"""
dev_tools/test_extraction.py
Sprint 4 — Standalone candidate field extraction tester.

Tests the full chain:
    raw_text  →  date_extraction_service  →  alert_service  →  structured payload

Usage:
    # Feed a raw text string directly
    ../venv/bin/python dev_tools/test_extraction.py "MFG 12/05/2026 EXP 12/11/2026 BATCH A123"

    # Run built-in test suite (no arguments)
    ../venv/bin/python dev_tools/test_extraction.py

NO camera. NO PaddleOCR. NO database. Pure text-in / structured-dict-out.
"""

from __future__ import annotations

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.date_extraction_service import extract_fields
from app.services.alert_service import process_ocr_result


# ── Built-in test cases ───────────────────────────────────────────────────────
BUILT_IN_CASES = [
    {
        "label": "Standard EAN label — DD/MM/YYYY",
        "raw_text": "MFG DATE 12/05/2026  EXP DATE 12/11/2026  BATCH NO A1234  MRP Rs.45.00",
        "confidence": 0.94,
    },
    {
        "label": "ISO date format — YYYY-MM-DD",
        "raw_text": "Manufactured: 2026-01-15\nBest Before: 2026-07-15\nLot No: L9876",
        "confidence": 0.88,
    },
    {
        "label": "Short year — DD/MM/YY",
        "raw_text": "PKD 10/03/26  USE BY 10/09/26  MRP 120",
        "confidence": 0.81,
    },
    {
        "label": "Textual month format",
        "raw_text": "Packed on 05 January 2026\nBest Before May 2026\nBatch: BT-990",
        "confidence": 0.91,
    },
    {
        "label": "Low confidence — triggers LOW_CONFIDENCE alert",
        "raw_text": "MFG 01/06/2026  EXP 01/12/2026",
        "confidence": 0.61,
    },
    {
        "label": "Missing expiry — triggers EXPIRY_NOT_FOUND alert",
        "raw_text": "MFG DATE 01/01/2026  BATCH NO XY99  MRP 80",
        "confidence": 0.89,
    },
    {
        "label": "Empty OCR — triggers OCR_FAILED alert",
        "raw_text": "",
        "confidence": 0.0,
    },
    {
        "label": "Ambiguous — many dates, minimal context",
        "raw_text": "01/01/2026 02/02/2026 03/03/2026 04/04/2026",
        "confidence": 0.85,
    },
]


def _run_case(label: str, raw_text: str, confidence: float) -> dict:
    ocr_result = {
        "raw_text":   raw_text,
        "confidence": confidence,
        "line_count": len(raw_text.splitlines()),
    }
    return process_ocr_result(ocr_result)


def _print_result(label: str, raw_text: str, confidence: float, result: dict) -> None:
    bar = "─" * 52
    print(f"\n┌{bar}┐")
    print(f"│  {label[:50]:<50}│")
    print(f"└{bar}┘")
    print(f"  Input text : {(raw_text[:70] + '…') if len(raw_text) > 70 else raw_text!r}")
    print(f"  Confidence : {confidence:.2f}")
    print()
    
    def _val(x):
        return x["value"] if x else "None"
        
    mfg = result['manufacturing_information']['mfg_date']
    exp = result['expiry_information']['expiry_date']
    pkd = result['manufacturing_information']['pkd_date']
    bb = result['expiry_information']['best_before']
    batch = result['manufacturing_information']['batch']
    lot = result['manufacturing_information']['lot']
    mrp = result['pricing_information']['mrp']
    
    print(f"  candidate_mfg_date    : {_val(mfg)}")
    print(f"  candidate_expiry_date : {_val(exp)}")
    print(f"  candidate_pkd_date    : {_val(pkd)}")
    print(f"  candidate_best_before : {_val(bb)}")
    print(f"  candidate_batch       : {_val(batch)}")
    print(f"  candidate_lot         : {_val(lot)}")
    print(f"  candidate_mrp         : {_val(mrp)}")
    print(f"  all_dates_found       : {result['ocr_information']['all_dates_found']}")
    if result["alerts"]:
        print(f"\n  ⚠  Alerts ({len(result['alerts'])}):")
        for a in result["alerts"]:
            print(f"     [{a['code']}]  {a['detail']}")
    else:
        print("\n  ✔  No alerts.")
    print()


def main() -> None:
    print("\n════════════════════════════════════════════════════════")
    print("  Sprint 4 — Candidate Field Extraction Tester")
    print("════════════════════════════════════════════════════════")

    # ── Mode 1: CLI argument — test a single raw text string ─────────────────
    if len(sys.argv) > 1:
        raw_text   = " ".join(sys.argv[1:])
        confidence = 0.90  # default when testing ad-hoc strings
        result     = _run_case("CLI input", raw_text, confidence)
        _print_result("CLI input", raw_text, confidence, result)
        print("── Full JSON payload ────────────────────────────────")
        print(json.dumps(result, indent=2, default=str))
        return

    # ── Mode 2: run built-in test suite ──────────────────────────────────────
    print(f"  Running {len(BUILT_IN_CASES)} built-in test cases…\n")
    passed = 0
    for case in BUILT_IN_CASES:
        result = _run_case(**case)
        _print_result(case["label"], case["raw_text"], case["confidence"], result)
        passed += 1

    print(f"════════ {passed}/{len(BUILT_IN_CASES)} test cases completed ════════\n")


if __name__ == "__main__":
    main()
