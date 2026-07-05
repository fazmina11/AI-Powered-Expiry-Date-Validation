"""
services/date_roi_service.py
Sprint 5 — Heuristic Date Region of Interest (ROI) detector & preprocessor.
Uses the existing EasyOCR instance to locate date text/keywords, crops
tightly, and cleans up the image for high-accuracy targeted Vision LLM calls.
"""

from __future__ import annotations

import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import cv2
import numpy as np
import re
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# List of keywords typically printed near dates on product labels
DATE_KEYWORDS = ['MFG', 'MFD', 'EXP', 'EXPIRY', 'USE BY', 'BB', 'BEST BEFORE', 'BATCH']
DATE_PATTERN = re.compile(r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{2,4}[/\-.]\d{1,2}[/\-.]\d{1,2}')


def _get_reader_instance():
    """
    Import and reuse the singleton EasyOCR reader from paddle_ocr_service.
    If it fails to import, lazy-initializes a fallback CPU reader.
    """
    try:
        from app.services.paddle_ocr_service import _get_reader
        return _get_reader()
    except Exception as e:
        logger.warning("[DateROI] Could not import _get_reader from paddle_ocr_service: %s. Loading fallback.", e)
        import easyocr
        return easyocr.Reader(['en'], gpu=False)


def find_date_regions(image_bgr: np.ndarray) -> list[list[list[int]]]:
    """
    Run EasyOCR's detector across the full image, then keep only boxes
    whose text looks like a date or a date-label keyword.
    Returns a list of bounding boxes in original image coordinates.
    """
    try:
        reader = _get_reader_instance()
        results = reader.readtext(image_bgr, detail=1)  # [(bbox, text, conf), ...]
    except Exception as exc:
        logger.error("[DateROI] EasyOCR text detection failed: %s", exc, exc_info=True)
        return []

    candidate_boxes = []
    for bbox, text, conf in results:
        text_upper = text.upper().strip()
        if any(kw in text_upper for kw in DATE_KEYWORDS) or DATE_PATTERN.search(text_upper):
            candidate_boxes.append(bbox)

    return candidate_boxes


def merge_and_pad_boxes(boxes: list[list[list[int]]], image_shape: tuple[int, ...], padding_ratio: float = 0.4) -> tuple[int, int, int, int] | None:
    """
    Merge nearby candidate boxes into one bounding region (dates and their
    labels are usually printed close together).
    Since dates are usually to the RIGHT or BELOW the keywords, we pad aggressively in those directions.
    """
    if not boxes:
        return None

    all_points = np.array([pt for box in boxes for pt in box])
    x_min, y_min = all_points.min(axis=0)
    x_max, y_max = all_points.max(axis=0)

    w = x_max - x_min
    h = y_max - y_min
    
    # Aggressive padding:
    # Left: 0.5x width (min 30px)
    # Right: 3.0x width (min 150px) to catch long dates to the right
    # Top: 0.5x height (min 30px)
    # Bottom: 2.0x height (min 100px) to catch dates on the next line
    pad_left = max(w * 0.5, 30)
    pad_right = max(w * 3.0, 150)
    pad_top = max(h * 0.5, 30)
    pad_bottom = max(h * 2.0, 100)

    img_h, img_w = image_shape[:2]
    x_min_val = max(0, int(x_min - pad_left))
    y_min_val = max(0, int(y_min - pad_top))
    x_max_val = min(img_w, int(x_max + pad_right))
    y_max_val = min(img_h, int(y_max + pad_bottom))

    return (x_min_val, y_min_val, x_max_val, y_max_val)


def preprocess_date_crop(crop_bgr: np.ndarray) -> np.ndarray:
    """
    Returns the original crop with slight contrast enhancement.
    Excessive upscaling/denoising destroys EasyOCR's ability to read dot-matrix text.
    """
    if crop_bgr.size == 0:
        return crop_bgr

    # Mild contrast limited adaptive histogram equalization (CLAHE) on the L channel
    lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    enhanced_bgr = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced_bgr


def extract_date_crop(
    image_bgr: np.ndarray,
    ocr_blocks: Optional[list[dict]] = None,
    barcode: Optional[str] = None
) -> tuple[bytes | None, bool]:
    """
    Main entry point. Returns (crop_bytes, found: bool).
    crop_bytes is a JPEG-encoded, preprocessed crop ready for the Vision LLM.
    If no candidate regions are found, returns (None, False).
    """
    if image_bgr is None or image_bgr.size == 0:
        return None, False

    # ── Try manual hint first if available ──
    if barcode:
        try:
            import json
            hints_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "sku_roi_hints.json")
            )
            if os.path.exists(hints_path):
                with open(hints_path, "r") as f:
                    hints = json.load(f)
                if barcode in hints:
                    hint = hints[barcode]
                    img_h, img_w = image_bgr.shape[:2]
                    x = int(hint["x"] * img_w)
                    y = int(hint["y"] * img_h)
                    w = int(hint["w"] * img_w)
                    h = int(hint["h"] * img_h)
                    
                    x_min = max(0, x)
                    y_min = max(0, y)
                    x_max = min(img_w, x + w)
                    y_max = min(img_h, y + h)
                    
                    if (x_max - x_min) > 10 and (y_max - y_min) > 10:
                        crop = image_bgr[y_min:y_max, x_min:x_max]
                        processed = preprocess_date_crop(crop)
                        success, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        if success:
                            logger.info("[ROI] Used manual coordinate crop hint for barcode %s: x=%d, y=%d, w=%d, h=%d",
                                        barcode, x, y, w, h)
                            return buffer.tobytes(), True
        except Exception as e:
            logger.warning("[ROI] Failed loading manual SKU ROI hint: %s", e)

    # Reconstruct bounding boxes from pre-extracted OCR blocks if available
    if ocr_blocks is not None:
        candidate_boxes = []
        for block in ocr_blocks:
            text_upper = block.get("text", "").upper().strip()
            if any(kw in text_upper for kw in DATE_KEYWORDS) or DATE_PATTERN.search(text_upper):
                x_min = block.get("x_min", 0.0)
                y_min = block.get("y_min", 0.0)
                x_max = block.get("x_max", 0.0)
                y_max = block.get("y_max", 0.0)
                candidate_boxes.append([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]])
        boxes = candidate_boxes
    else:
        boxes = find_date_regions(image_bgr)

    region = merge_and_pad_boxes(boxes, image_bgr.shape)

    if region is None:
        return None, False

    x_min, y_min, x_max, y_max = region
    crop = image_bgr[y_min:y_max, x_min:x_max]
    processed = preprocess_date_crop(crop)

    success, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not success:
        return None, False

    return buffer.tobytes(), True


def crop_to_base64(crop_bytes: bytes) -> str:
    """Encode raw cropped image bytes to base64 string."""
    return base64.b64encode(crop_bytes).decode('utf-8')


def is_frame_usable(frame: np.ndarray, blur_threshold: float = 10.0, glare_threshold: float = 0.25, occlusion_threshold: float = 0.45) -> tuple[bool, str]:
    """
    Evaluates whether the frame has sufficient quality (no excessive blur, glare, or hand occlusion).
    Returns (is_usable, reason_or_empty_str).
    """
    if frame is None or frame.size == 0:
        return False, "Empty or invalid frame"

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 30, 60], dtype=np.uint8)
    upper_skin = np.array([17, 140, 240], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
    skin_pixels = np.sum(skin_mask > 0)
    total_pixels = frame.shape[0] * frame.shape[1]
    skin_ratio = skin_pixels / total_pixels
    if skin_ratio > occlusion_threshold:
        return False, f"Obstruction detected (hand/fingers cover {skin_ratio:.1%})"

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance < blur_threshold:
        return False, f"Blurry (variance: {variance:.1f} < {blur_threshold})"

    saturated_pixels = np.sum(gray >= 250)
    saturated_ratio = saturated_pixels / total_pixels
    if saturated_ratio > glare_threshold:
        return False, f"Severe glare ({saturated_ratio:.1%} > {glare_threshold:.1%})"

    return True, ""
