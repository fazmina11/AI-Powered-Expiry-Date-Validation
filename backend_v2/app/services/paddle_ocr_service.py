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

def _preprocess_for_ocr(image_path: str) -> "np.ndarray":
    """
    Load and preprocess an image for best OCR accuracy.
    Applies: upscaling, glare removal, CLAHE contrast enhancement, sharpening, denoising.
    Returns a BGR numpy array ready for EasyOCR.
    """
    import cv2
    import numpy as np

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"cv2.imread returned None for: {image_path}")

    h, w = img.shape[:2]

    # 1. Upscale small images — OCR accuracy drops significantly below ~800px height
    min_side = min(h, w)
    if min_side < 800:
        scale = 800 / min_side
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        h, w = img.shape[:2]

    # 2. Remove glare / blown-out highlights via inpainting
    gray_tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, glare_mask = cv2.threshold(gray_tmp, 245, 255, cv2.THRESH_BINARY)
    if np.sum(glare_mask) > 0:
        kernel_g = np.ones((3, 3), np.uint8)
        glare_mask = cv2.dilate(glare_mask, kernel_g, iterations=1)
        img = cv2.inpaint(img, glare_mask, 3, cv2.INPAINT_TELEA)

    # 3. CLAHE contrast enhancement in LAB space (preserves colour, lifts dim labels)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b_ch = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    img = cv2.cvtColor(cv2.merge((l, a, b_ch)), cv2.COLOR_LAB2BGR)

    # 4. Unsharp masking — sharpens text edges
    blurred = cv2.GaussianBlur(img, (0, 0), 2.0)
    img = cv2.addWeighted(img, 2.0, blurred, -1.0, 0)

    # 5. Light denoising (keeps text sharp while smoothing sensor noise)
    img = cv2.fastNlMeansDenoisingColored(img, None, h=6, hColor=6, templateWindowSize=7, searchWindowSize=21)

    return img


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

    # Apply preprocessing to improve OCR on noisy / small / glary label images
    try:
        import cv2
        preprocessed = _preprocess_for_ocr(image_path)
        results = reader.readtext(preprocessed, detail=1)
        logger.info("[OCR] Used preprocessed image for EasyOCR. path=%s", image_path)
    except Exception as pre_exc:
        logger.warning("[OCR] Preprocessing failed (%s), falling back to raw file.", pre_exc)
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
    blocks: list[dict] = []

    for box, text, confidence in results:
        if text.strip():
            clean_texts.append(text.strip())
            clean_scores.append(float(confidence))
            
            # Extract axis-aligned bounding box coordinates
            try:
                x_coords = [float(pt[0]) for pt in box]
                y_coords = [float(pt[1]) for pt in box]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
            except Exception:
                x_min, y_min, x_max, y_max = 0.0, 0.0, 0.0, 0.0

            blocks.append({
                "text": text.strip(),
                "confidence": round(float(confidence), 4),
                "x_min": round(x_min, 1),
                "y_min": round(y_min, 1),
                "x_max": round(x_max, 1),
                "y_max": round(y_max, 1)
            })

    raw_text   = "\n".join(clean_texts)
    confidence = round(sum(clean_scores) / len(clean_scores), 4) if clean_scores else 0.0

    return {
        "raw_text":   raw_text,
        "confidence": confidence,
        "line_count": len(clean_texts),
        "image_path": image_path,
        "blocks":     blocks,
    }
