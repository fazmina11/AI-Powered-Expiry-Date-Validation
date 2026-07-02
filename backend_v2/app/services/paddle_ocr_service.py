"""
services/paddle_ocr_service.py
Sprint 3 — Raw OCR text extraction using EasyOCR (stable PyTorch fallback for CPU execution).

Responsibilities:
    - Load EasyOCR reader exactly once (module-level singleton).
    - Expose extract_text(image_path) → {"raw_text": "...", "confidence": 0.91}
"""

from __future__ import annotations

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Singleton ─────────────────────────────────────────────────────────────────
_reader: Optional[any] = None


def _get_reader():
    """
    Lazy-initialise and return the shared EasyOCR Reader.
    Downloads English model weights on first run (~15 MB, cached locally).
    """
    global _reader
    if _reader is None:
        import easyocr
        # Disable verbose warnings
        logging.getLogger('easyocr').setLevel(logging.WARNING)
        _reader = easyocr.Reader(['en'], gpu=False)  # Run on CPU stably
    return _reader


# ── Public API ────────────────────────────────────────────────────────────────

def extract_text(image_path: str) -> dict:
    """
    Run EasyOCR on a single image and return aggregated raw text.

    Returns:
        {
            "raw_text":   "MFG 01/05/2026 EXP 01/11/2026 BATCH A123",
            "confidence": 0.93,
            "line_count": 3,
            "image_path": "/abs/path"
        }
    """
    image_path = os.path.abspath(image_path)

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    reader = _get_reader()

    # EasyOCR readtext returns: [([box], text, confidence), ...]
    results = reader.readtext(image_path)

    if not results:
        return {
            "raw_text":   "",
            "confidence": 0.0,
            "line_count": 0,
            "image_path": image_path,
        }

    clean_texts: list[str] = []
    clean_scores: list[float] = []

    for box, text, confidence in results:
        if text.strip():
            clean_texts.append(text.strip())
            clean_scores.append(float(confidence))

    raw_text   = "\n".join(clean_texts)
    confidence = round(sum(clean_scores) / len(clean_scores), 4) if clean_scores else 0.0

    return {
        "raw_text":   raw_text,
        "confidence": confidence,
        "line_count": len(clean_texts),
        "image_path": image_path,
    }
