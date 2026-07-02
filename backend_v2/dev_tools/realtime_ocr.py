"""
dev_tools/realtime_ocr.py
Sprint 5 — CPU-Optimized Realtime Product Scanner with Multi-Frame Burst, Bounding Box Hints & Manual Fallback

Controls:
    SPACE   — Capture a burst of 6 frames, select the best one, and run scan pipeline
    H       — Draw a manual crop region (hint) around the date code on the packet
    M       — Open manual entry form fallback (writes directly to DB as manual_entry/marked_na)
    R       — Resume live webcam feed (clears current results)
    Q/ESC   — Quit
"""

from __future__ import annotations

import os
import sys
import cv2
import time
import json
import argparse
import tempfile
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# ── Colours & Font ────────────────────────────────────────────────────────────
GREEN   = (0, 220, 80)
CYAN    = (255, 220, 0)
YELLOW  = (0, 200, 255)
RED     = (0, 60, 220)
WHITE   = (255, 255, 255)
GREY    = (160, 160, 160)
BLACK   = (0, 0, 0)
FONT    = cv2.FONT_HERSHEY_SIMPLEX


# ── HUD Overlay ───────────────────────────────────────────────────────────────

def _draw_overlay(frame, barcode_raw: str | None, gs1: dict | None, off_data: dict | None,
                  ocr_res: dict | None, status: str, processing: bool, live_warnings: dict = None):
    h, w = frame.shape[:2]

    # Top Status Bar
    bar = frame.copy()
    cv2.rectangle(bar, (0, 0), (w, 46), BLACK, -1)
    cv2.addWeighted(bar, 0.7, frame, 0.3, 0, frame)

    status_col = YELLOW if processing else CYAN
    cv2.putText(frame, f"  {status}", (10, 30), FONT, 0.52, status_col, 1, cv2.LINE_AA)
    
    hint = "SPACE=Scan   R=Resume   Q=Quit"
    if barcode_raw:
        hint += "   H=Hint   M=Manual"
    cv2.putText(frame, hint, (w - 430, 30), FONT, 0.44, WHITE, 1, cv2.LINE_AA)

    # Live guide box in the center (only on live feed)
    if live_warnings is not None:
        box_x1, box_y1 = int(w/2 - 240), int(h/2 - 140)
        box_x2, box_y2 = int(w/2 + 240), int(h/2 + 140)
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), CYAN, 2)
        cv2.putText(frame, "ALIGN EXP/MFG DATE HERE", (box_x1 + 10, box_y1 - 10), FONT, 0.5, CYAN, 1, cv2.LINE_AA)

        # Draw warnings on screen
        if live_warnings.get("occlusion"):
            cv2.rectangle(frame, (int(w/2 - 200), 60), (int(w/2 + 200), 105), RED, -1)
            cv2.putText(frame, "WARNING: MOVE FINGER", (int(w/2 - 135), 90), FONT, 0.65, WHITE, 2, cv2.LINE_AA)
        elif live_warnings.get("glare"):
            cv2.rectangle(frame, (int(w/2 - 280), 60), (int(w/2 + 280), 105), RED, -1)
            cv2.putText(frame, "WARNING: REDUCE GLARE - TILT PACKET", (int(w/2 - 260), 90), FONT, 0.65, WHITE, 2, cv2.LINE_AA)
        elif live_warnings.get("blur"):
            cv2.rectangle(frame, (int(w/2 - 200), 60), (int(w/2 + 200), 105), YELLOW, -1)
            cv2.putText(frame, "WARNING: HOLD STILL / BLURRY", (int(w/2 - 170), 90), FONT, 0.65, BLACK, 2, cv2.LINE_AA)

    # Bottom Results Panel
    has_data = barcode_raw or gs1 or off_data or ocr_res
    if not has_data:
        return frame

    panel_h = 240
    panel = frame.copy()
    cv2.rectangle(panel, (0, h - panel_h), (w, h), BLACK, -1)
    cv2.addWeighted(panel, 0.78, frame, 0.22, 0, frame)
    cv2.line(frame, (0, h - panel_h), (w, h - panel_h), (70, 70, 70), 1)

    y  = h - panel_h + 28
    lh = 30

    def row(label, val, col=WHITE):
        nonlocal y
        if val:
            cv2.putText(frame, f"  {label:<18}: {str(val)}", (10, y),
                        FONT, 0.52, col, 1, cv2.LINE_AA)
            y += lh

    if barcode_raw:
        row("Barcode", barcode_raw, CYAN)

    if gs1:
        row("GTIN (BC)",     gs1.get("gtin"),         GREY)
        row("MFG Date (BC)", gs1.get("mfg_date"),     GREEN)
        row("EXP Date (BC)", gs1.get("expiry_date"),  GREEN)
        row("Batch (BC)",    gs1.get("batch_number"), WHITE)

    if off_data:
        row("Product",       off_data.get("product_name"), WHITE)
        row("Brand",         off_data.get("brand"),  GREY)
        row("Weight",        off_data.get("weight"), GREY)

    if ocr_res:
        exp  = ocr_res.get("expiry_date")
        mfg  = ocr_res.get("mfg_date")
        conf = float(ocr_res.get("confidence") or 0.0)
        source = ocr_res.get("source") or "Vision LLM"
        
        # Annotate if computed or manual
        if exp and ocr_res.get("exp_computed"):
            exp = f"{exp} (Computed)"

        row("Source",        source, CYAN)
        row("MFG Date (OCR)", mfg,  GREEN)
        row("EXP Date (OCR)", exp,  GREEN)
        row("Batch (OCR)",    ocr_res.get("batch_number"), WHITE)
        if conf:
            row("Confidence", f"{conf:.0%}", GREEN if conf >= 0.7 else YELLOW)

    return frame


# ── Tkinter Manual Form Fallback UI ───────────────────────────────────────────

def show_manual_entry_form(barcode: str) -> dict | None:
    """Spawns a native Tkinter modal dialog form for manual data entry."""
    root = tk.Tk()
    root.withdraw() # Hide root window
    
    dialog = tk.Toplevel(root)
    dialog.title(f"Manual Input — Barcode: {barcode}")
    dialog.geometry("450x380")
    dialog.resizable(False, False)
    
    # Stay on top and grab focus
    dialog.focus_force()
    dialog.grab_set()
    
    mfg_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    exp_var = tk.StringVar()
    batch_var = tk.StringVar()
    na_var = tk.BooleanVar(value=False)
    na_reason_var = tk.StringVar(value="NON_PERISHABLE")
    
    result_container = []

    frame = ttk.Frame(dialog, padding="15")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Automated Extraction Incomplete", font=("Helvetica", 11, "bold"), foreground="red").pack(anchor="w", pady=(0, 5))
    ttk.Label(frame, text="Please input product details manually:").pack(anchor="w", pady=(0, 15))

    grid = ttk.Frame(frame)
    grid.pack(fill="x", pady=5)

    ttk.Label(grid, text="MFG Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=5)
    mfg_entry = ttk.Entry(grid, textvariable=mfg_var, width=25)
    mfg_entry.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(grid, text="EXP Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
    exp_entry = ttk.Entry(grid, textvariable=exp_var, width=25)
    exp_entry.grid(row=1, column=1, sticky="w", pady=5)

    ttk.Label(grid, text="Batch Number:").grid(row=2, column=0, sticky="w", pady=5)
    batch_entry = ttk.Entry(grid, textvariable=batch_var, width=25)
    batch_entry.grid(row=2, column=1, sticky="w", pady=5)

    # N/A Frame
    na_frame = ttk.LabelFrame(frame, text="Expiry Not Applicable", padding="10")
    na_frame.pack(fill="x", pady=15)

    na_combo = None

    def on_na_toggle():
        if na_var.get():
            mfg_entry.config(state="disabled")
            exp_entry.config(state="disabled")
            na_combo.config(state="readonly")
        else:
            mfg_entry.config(state="normal")
            exp_entry.config(state="normal")
            na_combo.config(state="disabled")

    na_check = ttk.Checkbutton(na_frame, text="Mark as No Expiry / Not Applicable", variable=na_var, command=on_na_toggle)
    na_check.pack(anchor="w")

    reason_row = ttk.Frame(na_frame)
    reason_row.pack(fill="x", pady=(5, 0))
    ttk.Label(reason_row, text="Reason:").pack(side="left", padx=(0, 10))
    na_combo = ttk.Combobox(reason_row, textvariable=na_reason_var, values=["NON_PERISHABLE", "DATE_NOT_APPLICABLE", "OTHER"], state="disabled", width=25)
    na_combo.pack(side="left", fill="x", expand=True)

    # Buttons
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(side="bottom", anchor="e", pady=(10, 0))

    def on_submit():
        if not na_var.get():
            mfg_val = mfg_var.get().strip()
            exp_val = exp_var.get().strip()

            if not exp_val:
                messagebox.showerror("Validation Error", "EXP Date is required if not marked N/A.", parent=dialog)
                return

            for val, label in [(mfg_val, "MFG Date"), (exp_val, "EXP Date")]:
                if val:
                    try:
                        datetime.strptime(val, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Validation Error", f"Invalid format for {label}. Please use YYYY-MM-DD.", parent=dialog)
                        return

        result_container.append({
            "mfg_date": mfg_var.get().strip() if not na_var.get() else None,
            "expiry_date": exp_var.get().strip() if not na_var.get() else None,
            "batch_number": batch_var.get().strip() or None,
            "is_na": na_var.get(),
            "na_reason": na_reason_var.get() if na_var.get() else None
        })
        dialog.destroy()
        root.destroy()

    def on_cancel():
        dialog.destroy()
        root.destroy()

    ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side="right", padx=(5, 0))
    ttk.Button(btn_frame, text="Submit", command=on_submit).pack(side="right")

    dialog.wait_window()
    return result_container[0] if result_container else None


# ── DB Intake Manual Fallback Logic ───────────────────────────────────────────

def save_manual_entry(barcode: str, form_data: dict) -> bool:
    """Saves manual entry or marked N/A details to inventory_items and logs event."""
    from app.database import SessionLocal
    from app.models.product import Product
    from app.models.inventory_item import InventoryItem
    from app.models.manual_fallback_event import ManualFallbackEvent

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.barcode == barcode).first()
        if not product:
            # Create a draft fallback product if not in catalog
            product = Product(
                barcode=barcode,
                name=f"Draft Product ({barcode})",
                brand="Draft Brand",
                sku=f"SKU-{barcode}",
                is_active=True
            )
            db.add(product)
            db.flush()

        mfg_dt = None
        if form_data.get("mfg_date"):
            mfg_dt = datetime.strptime(form_data["mfg_date"], "%Y-%m-%d").date()

        exp_dt = None
        if form_data.get("expiry_date"):
            exp_dt = datetime.strptime(form_data["expiry_date"], "%Y-%m-%d").date()

        # Create Inventory Item
        item = InventoryItem(
            product_id=product.id,
            batch_number=form_data.get("batch_number"),
            manufacturing_date=mfg_dt,
            expiry_date=exp_dt,
            date_source="marked_na" if form_data["is_na"] else "manual_entry",
            na_reason=form_data["na_reason"] if form_data["is_na"] else None,
            pipeline_status="ML_COMPLETED",  # manual entry resolves the review process
            status_reason="Manual override by operator"
        )
        db.add(item)
        db.flush()

        # Log Fallback Event
        event = ManualFallbackEvent(
            barcode=barcode,
            resolved_status="marked_na" if form_data["is_na"] else "manual_entry",
            input_mfg_date=mfg_dt,
            input_expiry_date=exp_dt,
            input_batch=form_data.get("batch_number"),
            na_reason=form_data["na_reason"] if form_data["is_na"] else None
        )
        db.add(event)

        db.commit()
        print(f"[Manual Entry] Saved to DB. Event logged for barcode {barcode}.", flush=True)
        return True
    except Exception as e:
        db.rollback()
        print(f"[ERROR Manual Entry Save] DB error: {e}", flush=True)
        return False
    finally:
        db.close()


# ── Background Burst Processing Pipeline Worker ───────────────────────────────

def _run_burst_extraction(frames: list[np.ndarray], out_container: list):
    """
    Evaluates all burst frames using is_frame_usable, filters out failures,
    sorts by sharpness, and runs ScanPipelineService on candidates.
    """
    try:
        from app.services.date_roi_service import is_frame_usable
        from app.services.scan_pipeline_service import ScanPipelineService

        usable_frames = []
        last_reject_reason = "No frames captured"

        for idx, f in enumerate(frames):
            usable, reason = is_frame_usable(f)
            if usable:
                # Calculate Laplacian variance (sharpness)
                gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                variance = cv2.Laplacian(gray, cv2.CV_64F).var()
                usable_frames.append((f, variance, idx))
            else:
                last_reject_reason = reason

        # If no frames are usable, reject the burst
        if not usable_frames:
            out_container.append({
                "status": "FAILED_QUALITY",
                "reject_reason": last_reject_reason
            })
            return

        # Sort passing frames by sharpness descending
        usable_frames.sort(key=lambda x: x[1], reverse=True)

        pipeline = ScanPipelineService()
        
        # Process the top candidate frames in sequence
        # If the first sharpest frame misses dates or fails, fall back to the next-sharpest.
        for candidate_frame, var, idx in usable_frames[:3]:
            print(f"[Burst Worker] Evaluating frame {idx} (sharpness: {var:.1f})...", flush=True)
            res = pipeline.process_scan(image=candidate_frame)
            
            # Check if successful extraction occurred
            has_expiry = False
            if res.expiry and res.expiry.expiry_date:
                has_expiry = True

            if res.status in ("SUCCESS", "PARTIAL_SUCCESS") and has_expiry:
                out_container.append({
                    "status": "SUCCESS",
                    "barcode": res.barcode.value if res.barcode else None,
                    "product_name": res.product.name,
                    "brand": res.product.brand,
                    "mfg_date": res.manufacturing.manufacturing_date,
                    "expiry_date": res.expiry.expiry_date,
                    "batch_number": res.batch.batch_number,
                    "source": res.expiry.raw_text or "Combination Pipeline",
                    "confidence": res.ocr.confidence or 0.8,
                    "exp_computed": res.exp_computed,
                    "frame": candidate_frame
                })
                return

        # If all candidates failed
        fallback_frame = usable_frames[0][0]  # Return the sharpest frame for manual box fallback
        out_container.append({
            "status": "FAILED_NO_DATES",
            "barcode": res.barcode.value if 'res' in locals() and res.barcode else None,
            "product_name": res.product.name if 'res' in locals() and res.product else None,
            "brand": res.product.brand if 'res' in locals() and res.product else None,
            "frame": fallback_frame
        })

    except Exception as exc:
        print(f"[Burst Worker] Pipeline failure: {exc}")
        out_container.append({"status": "ERROR", "msg": str(exc)})


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()

    # Use DirectShow on Windows first, fallback to default if unsupported
    cap = None
    if sys.platform == "win32":
        print("[INFO] Initializing DirectShow camera backend...", flush=True)
        cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ok, _ = cap.read()
            if not ok:
                print("[WARNING] DirectShow failed to capture frame. Re-initializing default...", flush=True)
                cap.release()
                cap = None

    if cap is None or not cap.isOpened():
        print("[INFO] Initializing default camera backend...", flush=True)
        cap = cv2.VideoCapture(args.camera)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ok, _ = cap.read()
            if not ok:
                print("[WARNING] Setting custom resolution failed. Re-initializing default settings...", flush=True)
                cap.release()
                cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {args.camera}")
        sys.exit(1)

    # Warm up camera sensor
    print("[INFO] Warming up camera sensor...", flush=True)
    for _ in range(10):
        cap.read()
        time.sleep(0.05)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Realtime Product Scanner — CPU-Burst & Manual Fallback  ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  1. Hold product steady in front of camera.              ║")
    print("║  2. Press SPACE to trigger best-of-N capture.            ║")
    print("║  3. If dates are missed, press H (Hint) or M (Manual).   ║")
    print("║  4. Press R to resume live camera feed.                  ║")
    print("║  5. Press Q to quit.                                     ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    frozen_frame   = None
    barcode_raw    = None
    gs1_data       = None
    off_data       = None
    ocr_res        = None
    status         = "LIVE — Point camera at label, then press SPACE"
    processing     = False
    fail_count     = 0

    live_warnings = {"occlusion": False, "glare": False, "blur": False}

    while True:
        if frozen_frame is None:
            ok, frame = cap.read()
            if not ok or frame is None:
                fail_count += 1
                if fail_count > 30:
                    print("[ERROR] Camera disconnected or stopped sending frames.", flush=True)
                    break
                time.sleep(0.03)
                continue
            fail_count = 0
            
            # Reset live warnings and check frame usability
            live_warnings = {"occlusion": False, "glare": False, "blur": False}
            try:
                from app.services.date_roi_service import is_frame_usable
                usable, reason = is_frame_usable(frame)
                if not usable:
                    if "Obstruction" in reason or "hand" in reason:
                        live_warnings["occlusion"] = True
                    if "glare" in reason:
                        live_warnings["glare"] = True
                    if "Blurry" in reason:
                        live_warnings["blur"] = True
            except Exception:
                pass

            display = frame.copy()
        else:
            display = frozen_frame.copy()

        display = _draw_overlay(
            display,
            barcode_raw,
            gs1_data,
            off_data,
            ocr_res,
            status,
            processing,
            live_warnings=live_warnings if frozen_frame is None else None
        )

        cv2.imshow("Product Scanner", display)

        key = cv2.waitKey(1) & 0xFF

        # ── SPACE: Freeze frame & Run Scan Burst Pipeline ────────────────────
        if key == ord(" ") and not processing:
            status       = "CAPTURING BURST... Please hold still"
            processing   = True

            # Capture a burst of 6 frames over ~1 second to filter out transient blur/glare
            burst_frames = []
            for _ in range(6):
                time.sleep(0.12)
                ok, f = cap.read()
                if ok and f is not None:
                    burst_frames.append(f)

            if not burst_frames:
                status = "SCAN FAILED: Frame capture failed. Press R"
                processing = False
                continue

            frozen_frame = burst_frames[-1].copy()
            status       = "SCANNING BURST... Processing best candidates"

            container = []

            def _thread_worker():
                nonlocal processing, status, barcode_raw, gs1_data, off_data, ocr_res, frozen_frame
                _run_burst_extraction(burst_frames, container)
                
                result = container[0] if container else {}
                
                if result.get("status") == "SUCCESS":
                    barcode_raw = result.get("barcode")
                    
                    if result.get("source") == "gs1_datamatrix_direct":
                        gs1_data = {
                            "gtin": barcode_raw,
                            "mfg_date": result.get("mfg_date"),
                            "expiry_date": result.get("expiry_date"),
                            "batch_number": result.get("batch_number")
                        }
                    else:
                        ocr_res = {
                            "mfg_date": result.get("mfg_date"),
                            "expiry_date": result.get("expiry_date"),
                            "batch_number": result.get("batch_number"),
                            "source": result.get("source"),
                            "confidence": result.get("confidence"),
                            "exp_computed": result.get("exp_computed", False)
                        }
                        if result.get("product_name"):
                            off_data = {
                                "product_name": result.get("product_name"),
                                "brand": result.get("brand"),
                                "weight": None
                            }
                    
                    # Update displayed frame to the one that parsed successfully
                    if result.get("frame") is not None:
                        frozen_frame = result["frame"].copy()

                    status = "SCAN COMPLETE — Press R to scan another"

                elif result.get("status") == "FAILED_NO_DATES":
                    barcode_raw = result.get("barcode")
                    if result.get("product_name"):
                        off_data = {
                            "product_name": result.get("product_name"),
                            "brand": result.get("brand"),
                            "weight": None
                        }
                    if result.get("frame") is not None:
                        frozen_frame = result["frame"].copy()
                    
                    status = "EXP/MFG NOT FOUND — Press H (draw box) or M (manual entry)"

                elif result.get("status") == "FAILED_QUALITY":
                    status = f"QUALITY FAILED: {result.get('reject_reason')}. Press R"
                else:
                    status = f"SCAN FAILED: {result.get('msg', 'Unknown Error')}. Press R / M for manual fallback"
                
                processing = False

            threading.Thread(target=_thread_worker, daemon=True).start()

        # ── H: Draw Manual Bounding Box ──────────────────────────────────────
        elif key in (ord("h"), ord("H")) and not processing:
            if not barcode_raw:
                status = "ERROR: Scan barcode first before setting manual box!"
                continue

            if frozen_frame is None:
                status = "ERROR: Capture a frame using SPACE first!"
                continue

            print("[ROI] Opening ROI drawer window. Drag box and press ENTER/SPACE.")
            # Select ROI on the frozen frame
            rect = cv2.selectROI("Draw box around EXP/MFG dates, then press ENTER", frozen_frame, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow("Draw box around EXP/MFG dates, then press ENTER")
            
            x, y, w, h = rect
            if w > 10 and h > 10:
                img_h, img_w = frozen_frame.shape[:2]
                x_rel = x / img_w
                y_rel = y / img_h
                w_rel = w / img_w
                h_rel = h / img_h

                try:
                    hints_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "..", "uploads", "sku_roi_hints.json")
                    )
                    hints = {}
                    if os.path.exists(hints_path):
                        with open(hints_path, "r") as f:
                            hints = json.load(f)
                    
                    hints[barcode_raw] = {
                        "x": x_rel,
                        "y": y_rel,
                        "w": w_rel,
                        "h": h_rel
                    }
                    
                    os.makedirs(os.path.dirname(hints_path), exist_ok=True)
                    with open(hints_path, "w") as f:
                        json.dump(hints, f, indent=4)
                    
                    status = "ROI Hint Saved! Re-scanning frame..."
                    processing = True
                    
                    # Re-run pipeline on the frozen frame immediately using the hint
                    def _re_scan_worker():
                        nonlocal processing, status, barcode_raw, gs1_data, off_data, ocr_res
                        from app.services.scan_pipeline_service import ScanPipelineService
                        pipeline = ScanPipelineService()
                        res = pipeline.process_scan(image=frozen_frame)
                        
                        has_expiry = False
                        if res.expiry and res.expiry.expiry_date:
                            has_expiry = True

                        if res.status in ("SUCCESS", "PARTIAL_SUCCESS") and has_expiry:
                            ocr_res = {
                                "mfg_date": res.manufacturing.manufacturing_date,
                                "expiry_date": res.expiry.expiry_date,
                                "batch_number": res.batch.batch_number,
                                "source": res.expiry.raw_text or "Manual ROI Crop Hint",
                                "confidence": res.ocr.confidence or 0.9,
                                "exp_computed": res.exp_computed
                            }
                            status = "SCAN COMPLETE — Manual ROI Hint verified!"
                        else:
                            status = "ROI saved, but scanner still failed to find dates. Try again"
                        processing = False

                    threading.Thread(target=_re_scan_worker, daemon=True).start()
                except Exception as save_exc:
                    status = f"FAILED to save ROI: {save_exc}"
            else:
                status = "Cancelled manual box selection."

        # ── M: Manual Entry Fallback Form ────────────────────────────────────
        elif key in (ord("m"), ord("M")) and not processing:
            if not barcode_raw:
                status = "ERROR: Scan barcode first before manual fallback!"
                continue

            print("[Manual Form] Launching manual date entry form...", flush=True)
            form_res = show_manual_entry_form(barcode_raw)
            
            if form_res:
                saved = save_manual_entry(barcode_raw, form_res)
                if saved:
                    source_label = "manual_entry"
                    if form_res["is_na"]:
                        source_label = f"marked_na ({form_res['na_reason']})"
                        
                    ocr_res = {
                        "mfg_date": form_res["mfg_date"] or "N/A",
                        "expiry_date": form_res["expiry_date"] or "N/A",
                        "batch_number": form_res["batch_number"] or "N/A",
                        "source": source_label,
                        "confidence": 1.0,
                        "exp_computed": False
                    }
                    status = "MANUAL ENTRY SAVED — Press R to scan another product"
                else:
                    status = "ERROR: Failed to save manual entry to database."
            else:
                status = "Cancelled manual date override."

        # ── R: Resume live feed ───────────────────────────────────────────────
        elif key in (ord("r"), ord("R")) and not processing:
            frozen_frame   = None
            barcode_raw    = None
            gs1_data       = None
            off_data       = None
            ocr_res        = None
            status         = "LIVE — Point camera at label, then press SPACE"

        # ── Q / ESC: Quit ─────────────────────────────────────────────────────
        elif key in (ord("q"), ord("Q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Scanner closed.")


if __name__ == "__main__":
    main()
