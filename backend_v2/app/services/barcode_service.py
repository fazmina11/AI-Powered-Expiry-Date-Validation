"""
services/barcode_service.py
Sprint 1 — Camera → Barcode Detection

Responsibilities:
    - Accept an OpenCV frame (numpy array)
    - Decode all barcodes found in the frame using zxing-cpp
    - Return structured result dict or None

NO database. NO SQLAlchemy. NO FastAPI. NO product lookup.
Those integrations belong to Sprint 2+ (Member 2's pipeline).

NOTE: pyzbar was replaced by zxing-cpp because pyzbar's underlying
zbar C library has a memory alignment bug (SIGSEGV) on Apple Silicon
(ARM64/M1/M2/M3). zxing-cpp is a pure C++17 library with native
ARM64 support, no external system dependencies, and equivalent
detection quality.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import cv2
import numpy as np
import zxingcpp

logger = logging.getLogger(__name__)


class BarcodeService:
    """
    Stateless barcode detection service using a multi-stage preprocessing pipeline.
    """

    def detect(self, frame: np.ndarray, debug: bool = False) -> Optional[dict]:
        """
        Attempt to detect a barcode by passing the frame through multiple
        OpenCV preprocessing stages. Halts on first success.

        Uses zxing-cpp (NOT pyzbar) for Apple Silicon (ARM64) compatibility.
        pyzbar causes SIGSEGV on M1/M2/M3 due to a zbar C library alignment bug.
        """
        if frame is None or frame.size == 0:
            return None

        for stage_name, processed_frame in self._generate_preprocessed_frames(frame):
            if debug:
                logger.debug("[BarcodeService] Trying stage: %s", stage_name)

            try:
                barcodes = zxingcpp.read_barcodes(processed_frame)
            except Exception as exc:
                logger.warning("[BarcodeService] zxingcpp.read_barcodes failed at stage '%s': %s", stage_name, exc)
                continue

            if barcodes:
                if debug:
                    logger.debug("[BarcodeService] Barcode detected at stage: %s", stage_name)

                barcode = barcodes[0]

                # zxingcpp uses barcode.position (a quadrilateral) instead of barcode.rect
                pos = barcode.position
                xs = [p.x for p in [pos.top_left, pos.top_right, pos.bottom_right, pos.bottom_left]]
                ys = [p.y for p in [pos.top_left, pos.top_right, pos.bottom_right, pos.bottom_left]]
                x, y = min(xs), min(ys)
                w = max(xs) - x
                h = max(ys) - y

                return {
                    "barcode": barcode.text,
                    "barcode_type": barcode.format.name,
                    "detected": True,
                    "quality": 1,
                    "orientation": "UNKNOWN",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "rect": {
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                    },
                }

        if debug:
            logger.debug("[BarcodeService] No barcode detected in any stage.")

        return None

    def _generate_preprocessed_frames(self, frame: np.ndarray):
        """Lazy generator yielding (stage_name, image_buffer)."""
        # 1. Original frame
        yield "Original", frame

        # 2. Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        yield "Grayscale", gray

        # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl1 = clahe.apply(gray)
        yield "CLAHE", cl1

        # 4. Adaptive Threshold (after light blur)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh_adapt = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        yield "Adaptive Threshold", thresh_adapt

        # 5. Otsu Threshold
        _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        yield "Otsu Threshold", thresh_otsu

        # 6. Resize image (2x upscaling)
        resized = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        yield "Resized grayscale", resized

        # 7. Sharpen image
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        yield "Sharpened image", sharpened

    def draw_overlay(self, frame: np.ndarray, result: dict) -> np.ndarray:
        """Draw bounding box and label onto the frame."""
        rect = result["rect"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        label = f'{result["barcode"]} [{result["barcode_type"]}]'
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        return frame


# ══════════════════════════════════════════════════════════════════
#  DB-layer compatibility shims — used by Member 2's pipeline
#  (scan_session_service.py, ocr_routes.py)
#  DO NOT REMOVE.
# ══════════════════════════════════════════════════════════════════

from typing import Any
from sqlalchemy.orm import Session as _Session
from app.models.barcode_scan import BarcodeScan as _BarcodeScan
from app.models.product import Product as _Product


def process_barcode_scan(
    db: _Session,
    raw_barcode: str,
    barcode_type: Optional[str] = None,
    scan_source: Optional[str] = None,
    notes: Optional[str] = None,
) -> _BarcodeScan:
    """Resolve barcode to product catalogue and log a BarcodeScan event."""
    product = db.query(_Product).filter(
        _Product.barcode == raw_barcode,
        _Product.is_active == True,
    ).first()

    status = "resolved" if product else "unresolved"
    product_id = product.id if product else None

    scan_event = _BarcodeScan(
        product_id=product_id,
        raw_barcode=raw_barcode,
        barcode_type=barcode_type or "EAN13",
        scan_source=scan_source,
        scan_status=status,
        notes=notes,
    )
    db.add(scan_event)
    db.commit()
    db.refresh(scan_event)
    return scan_event


def get_scan_by_id(db: _Session, scan_id: Any) -> Optional[_BarcodeScan]:
    """Retrieve barcode scan record by UUID/ID."""
    return db.query(_BarcodeScan).filter(_BarcodeScan.id == scan_id).first()


def get_unresolved_scans(db: _Session, limit: int = 50):
    """Retrieve list of unresolved barcode scans."""
    return (
        db.query(_BarcodeScan)
        .filter(_BarcodeScan.scan_status == "unresolved")
        .order_by(_BarcodeScan.scanned_at.desc())
        .limit(limit)
        .all()
    )
