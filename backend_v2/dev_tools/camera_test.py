"""
dev_tools/camera_test.py
Phase 2 — OCR Primary Intake Engine

Flow:
    Camera opens
    ↓
    (Optional) Detect Barcode in background
    ↓
    Press SPACE  →  capture frame  →  save to uploads/labels/
    ↓
    Run PaddleOCR extraction on saved image
    ↓
    Run Regex Parser & Alert Engine
    ↓
    Print complete OCR DTO to terminal
    ↓
    Press Q to quit

Controls:
    SPACE  — capture label image & run OCR pipeline
    Q      — quit

Usage:
    cd backend_v2/
    ../venv/bin/python dev_tools/camera_test.py

This is a standalone dev tool.
NO routes. NO database writes.
"""

from __future__ import annotations

import os
import sys
import time
import json

# Allow importing from backend_v2/ regardless of cwd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import cv2
except ImportError:
    print("[ERROR] OpenCV not found.  Run: pip install opencv-python")
    sys.exit(1)

from app.services.barcode_service import BarcodeService
from app.services.image_capture_service import ImageCaptureService
from app.services.paddle_ocr_service import extract_text
from app.services.alert_service import process_ocr_result

# ── Overlay helpers ───────────────────────────────────────────────────────────

_FONT       = cv2.FONT_HERSHEY_SIMPLEX
_GREEN      = (0, 220, 0)
_WHITE      = (255, 255, 255)
_BLACK      = (0, 0, 0)
_YELLOW     = (0, 215, 255)


def _put(frame, text: str, pos: tuple, color=_WHITE, scale=0.6, thickness=2):
    """Draw text with a thin dark shadow for readability."""
    x, y = pos
    cv2.putText(frame, text, (x + 1, y + 1), _FONT, scale, _BLACK, thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y),         _FONT, scale, color,  thickness,     cv2.LINE_AA)


def draw_status(frame, barcode_result: dict | None) -> None:
    """
    Render all HUD overlays onto the frame in-place.
    """
    h, w = frame.shape[:2]
    margin = 12

    if barcode_result:
        rect = barcode_result["rect"]
        x, y, bw, bh = rect["x"], rect["y"], rect["w"], rect["h"]
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), _GREEN, 2)
        
        quality = barcode_result.get("quality", 1)
        _put(frame, f"{barcode_result['barcode']} [Q:{quality}]", (x, y - 8), _GREEN, 0.55, 2)

    _put(frame, "OCR Intake Engine", (margin, h - 44), _YELLOW, 0.65, 2)
    _put(frame, "SPACE = capture & extract   Q = quit", (margin, h - 14), _WHITE, 0.55, 2)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    barcode_svc = BarcodeService()
    capture_svc = ImageCaptureService()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not accessible.")
        print("  → System Settings > Privacy & Security > Camera")
        sys.exit(1)

    print()
    print("════════════════════════════════════")
    print("  Phase 2 — OCR Primary Engine")
    print("════════════════════════════════════")
    print("  SPACE  →  capture & run extraction")
    print("  Q      →  quit")
    print("════════════════════════════════════")
    print()

    last_result: dict | None = None   # optional barcode context

    while True:
        loop_start = time.time()
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        # ── Optional Barcode detection ────────────────────────────────────────
        # Temporarily disabled to prevent `zsh: segmentation fault` on macOS
        # caused by the underlying C-library (zbar) on M-series chips.
        # try:
        #     result = barcode_svc.detect(frame, debug=False)
        #     if result:
        #         last_result = result
        # except Exception as e:
        #     pass

        # ── HUD overlay ───────────────────────────────────────────────────────
        draw_status(frame, last_result)

        fps = 1.0 / (time.time() - loop_start)
        _put(frame, f"FPS: {fps:.1f}", (12, 24), _YELLOW, 0.6, 2)

        cv2.imshow("Phase 2 — OCR Primary Engine", frame)

        # ── Key handling ──────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord(" "):
            # Capture frame
            ret2, raw_frame = cap.read()
            snapshot = capture_svc.capture(raw_frame if ret2 else frame)
            saved_path = capture_svc.save(snapshot)
            print(f"\\n[SAVED] {saved_path}")
            print("[INFO] Running OCR Extraction Pipeline...")
            
            # Run Pipeline
            try:
                ocr_result = extract_text(saved_path)
                pipeline_result = process_ocr_result(ocr_result)
                
                # Add optional barcode
                if last_result:
                    pipeline_result["barcode"] = last_result["barcode"]
                
                # Print cleanly
                print("\\n════════ OCR EXTRACTED JSON DTO ════════")
                print(json.dumps(pipeline_result, indent=2))
                print("════════════════════════════════════════\\n")
            except Exception as e:
                print(f"[ERROR] Pipeline failed: {e}")

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Session ended.")


if __name__ == "__main__":
    main()
