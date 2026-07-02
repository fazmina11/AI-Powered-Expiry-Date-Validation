import time
import os
import cv2
import logging
import numpy as np
import tempfile
from typing import Any, Dict, Optional
from datetime import datetime

from app.schemas.product_intelligence_schema import ProductIntelligence
from app.schemas.validation_schema import ValidationResult
from app.schemas.alert_schema import AlertResult
from app.services.barcode_service import BarcodeService
from app.services.barcode_intelligence_service import BarcodeIntelligenceService
from app.services.product_lookup_service import ProductLookupService
from app.services.paddle_ocr_service import extract_text
from app.services.product_intelligence_service import ProductIntelligenceService
from app.services.validation_service import ValidationService
from app.services.date_extraction_service import extract_fields
from app.services.alert_service import AlertService
from app.services.vision_llm_service import (
    extract_structured_fields_from_text,
    extract_structured_fields_via_llm,
)

log = logging.getLogger("scan_pipeline")


class PipelineResult(ProductIntelligence):
    validation: Optional[ValidationResult] = None
    alerts: Optional[AlertResult] = None
    status: str = "FAILED"
    execution_times: Dict[str, float] = {}
    total_time: float = 0.0
    reject_reason: Optional[str] = None
    exp_computed: bool = False


class ScanPipelineService:
    def __init__(self):
        self.barcode_service = BarcodeService()
        self.barcode_intel_service = BarcodeIntelligenceService()
        self.product_lookup_service = ProductLookupService()
        self.product_intel_service = ProductIntelligenceService()
        self.validation_service = ValidationService()
        self.alert_service = AlertService()

    def process_scan(self, image: Any) -> PipelineResult:
        start_total = time.time()
        execution_times = {}

        barcode_raw = None
        barcode_data = None
        product_lookup = None
        ocr_data = None

        # Determine image source
        image_path = None
        frame = None
        temp_file_path = None  # Track separately so cleanup is explicit

        log.info("[Pipeline] === process_scan START ===")
        print("[Pipeline] === process_scan START ===", flush=True)

        if isinstance(image, str):
            image_path = image
            log.info("[Pipeline] Input: file path = %s", image_path)
            print(f"[Pipeline] Input: file path = {image_path}", flush=True)
            frame = cv2.imread(image_path)
            if frame is None:
                log.error("[Pipeline] cv2.imread returned None for path: %s", image_path)
                print(f"[Pipeline] ERROR: cv2.imread returned None for {image_path}", flush=True)

        elif isinstance(image, np.ndarray):
            frame = image
            log.info("[Pipeline] Input: numpy array, shape=%s", frame.shape)
            print(f"[Pipeline] Input: numpy array shape={frame.shape}", flush=True)
            try:
                # Use mkstemp: creates file, returns (fd, path).
                # Close the fd immediately so cv2.imwrite can open the path itself.
                fd, temp_file_path = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                result_ok = cv2.imwrite(temp_file_path, frame)
                if result_ok:
                    image_path = temp_file_path
                    log.info("[Pipeline] Frame written to temp file: %s", temp_file_path)
                    print(f"[Pipeline] Frame saved to temp: {temp_file_path}", flush=True)
                else:
                    log.error("[Pipeline] cv2.imwrite FAILED for: %s", temp_file_path)
                    print(f"[Pipeline] ERROR: cv2.imwrite failed for {temp_file_path}", flush=True)
            except Exception as exc:
                log.error("[Pipeline] Temp file creation failed: %s", exc, exc_info=True)
                print(f"[Pipeline] ERROR creating temp file: {exc}", flush=True)

        # ── Frame Quality Gating Check ───────────────────────────────────────
        if frame is not None:
            try:
                from app.services.date_roi_service import is_frame_usable
                usable, reason = is_frame_usable(frame)
                if not usable:
                    log.warning("[Pipeline] Quality gate FAILED: %s", reason)
                    print(f"[Pipeline] QUALITY GATE FAILED: {reason}", flush=True)
                    
                    # Cleanup temp file immediately on early exit
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                        except Exception:
                            pass

                    # Build an empty profile
                    profile = self.product_intel_service.build_product_profile()
                    total_time = time.time() - start_total
                    
                    return PipelineResult(
                        **profile.model_dump(),
                        status="FAILED_QUALITY",
                        reject_reason=reason,
                        total_time=total_time,
                        execution_times=execution_times
                    )
            except Exception as q_exc:
                log.warning("[Pipeline] Quality gating execution error: %s", q_exc)

        # ── Stage 0: GS1 DataMatrix Direct Check ──────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 0: GS1 DataMatrix direct check ---")
        print("[Pipeline] --- Stage 0: GS1 DataMatrix direct check ---", flush=True)
        gs1_result = None
        if frame is not None:
            try:
                from app.services.gs1_barcode_service import extract_dates_from_datamatrix
                gs1_result = extract_dates_from_datamatrix(frame)
            except Exception as gs1_exc:
                log.warning("[Pipeline] GS1 check failed: %s", gs1_exc)
                print(f"[Pipeline] GS1 check failed: {gs1_exc}", flush=True)
        execution_times["gs1_datamatrix"] = time.time() - t0

        # ── Stage 1: Barcode Detection ───────────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 1: Barcode Detection ---")
        print("[Pipeline] --- Stage 1: Barcode Detection ---", flush=True)
        try:
            if frame is not None:
                detect_result = self.barcode_service.detect(frame)
                if detect_result and "barcode" in detect_result:
                    barcode_raw = detect_result["barcode"]
                    log.info("[Pipeline] Barcode detected: %s", barcode_raw)
                    print(f"[Pipeline] Barcode detected: {barcode_raw}", flush=True)

                    # Check if the detected barcode string is a GS1-128 linear barcode
                    is_gs1 = False
                    if barcode_raw.startswith("("):
                        is_gs1 = True
                    elif len(barcode_raw) > 13 and (barcode_raw.startswith("01") or barcode_raw.startswith("17") or barcode_raw.startswith("11") or barcode_raw.startswith("10")):
                        is_gs1 = True
                    
                    if is_gs1:
                        try:
                            from app.services.gs1_barcode_service import parse_gs1_string, gs1_date_to_iso, AI_GTIN, AI_MFG_DATE, AI_EXP_DATE, AI_BATCH
                            log.info("[Pipeline] Routing linear barcode %s to GS1-128 parser", barcode_raw)
                            print(f"[Pipeline] Routing linear barcode {barcode_raw} to GS1-128 parser", flush=True)
                            fields = parse_gs1_string(barcode_raw)
                            gs1_result = {
                                'found': True,
                                'gtin': fields.get(AI_GTIN),
                                'mfg': gs1_date_to_iso(fields.get(AI_MFG_DATE)),
                                'exp': gs1_date_to_iso(fields.get(AI_EXP_DATE)),
                                'batch': fields.get(AI_BATCH),
                            }
                            if gs1_result.get("gtin"):
                                barcode_raw = gs1_result["gtin"]
                        except Exception as parse_exc:
                            log.warning("[Pipeline] GS1-128 parsing failed: %s", parse_exc)

                elif gs1_result and gs1_result.get("found") and gs1_result.get("gtin"):
                    barcode_raw = gs1_result.get("gtin")
                    log.info("[Pipeline] Using GTIN from GS1 DataMatrix: %s", barcode_raw)
                    print(f"[Pipeline] Using GTIN from GS1 DataMatrix: {barcode_raw}", flush=True)
                else:
                    log.info("[Pipeline] No barcode found in frame.")
                    print("[Pipeline] No barcode found in frame.", flush=True)
        except Exception as exc:
            log.error("[Pipeline] Barcode detection FAILED: %s", exc, exc_info=True)
            print(f"[Pipeline] ERROR barcode detection: {exc}", flush=True)
        execution_times["detect_barcode"] = time.time() - t0

        # ── Stage 2: Barcode Intelligence ───────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 2: Barcode Intelligence ---")
        print("[Pipeline] --- Stage 2: Barcode Intelligence ---", flush=True)
        if barcode_raw:
            try:
                barcode_data = self.barcode_intel_service.parse_barcode(barcode_raw)
                log.info("[Pipeline] Barcode intelligence OK.")
                print("[Pipeline] Barcode intelligence OK.", flush=True)
            except Exception as exc:
                log.error("[Pipeline] Barcode intelligence FAILED: %s", exc, exc_info=True)
                print(f"[Pipeline] ERROR barcode intelligence: {exc}", flush=True)
        else:
            log.info("[Pipeline] Skipping Barcode Intelligence (no barcode).")
            print("[Pipeline] Skipping Barcode Intelligence (no barcode).", flush=True)
        execution_times["barcode_intelligence"] = time.time() - t0

        # ── Stage 3: Product Lookup ──────────────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 3: Product Lookup ---")
        print("[Pipeline] --- Stage 3: Product Lookup ---", flush=True)
        if barcode_raw:
            try:
                product_lookup = self.product_lookup_service.lookup_product(barcode_raw)
                log.info("[Pipeline] Product lookup OK: found=%s", getattr(product_lookup, "found", None))
                print(f"[Pipeline] Product lookup OK.", flush=True)
            except Exception as exc:
                log.error("[Pipeline] Product lookup FAILED: %s", exc, exc_info=True)
                print(f"[Pipeline] ERROR product lookup: {exc}", flush=True)
        else:
            log.info("[Pipeline] Skipping Product Lookup (no barcode).")
            print("[Pipeline] Skipping Product Lookup (no barcode).", flush=True)
        execution_times["product_lookup"] = time.time() - t0

        # ── Stage 4: OCR + Date Extraction ──────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 4: OCR + Date Extraction ---")
        print("[Pipeline] --- Stage 4: OCR + Date Extraction ---", flush=True)
        try:
            # Keep partial GS1 details to merge later if needed
            partial_gs1 = gs1_result if (gs1_result and gs1_result.get("found")) else None

            # ── STAGE 4.0: Direct dates from GS1 DataMatrix ───────────────────
            if gs1_result and gs1_result.get("found") and gs1_result.get("mfg") and gs1_result.get("exp"):
                log.info("[Pipeline] Skipping OCR because dates are parsed directly from GS1 barcode!")
                print("[Pipeline] Skipping OCR (GS1 dates direct).", flush=True)

                mfg_iso = None
                exp_iso = None
                if gs1_result.get("mfg"):
                    try:
                        mfg_iso = datetime.strptime(gs1_result["mfg"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception:
                        mfg_iso = gs1_result["mfg"]
                if gs1_result.get("exp"):
                    try:
                        exp_iso = datetime.strptime(gs1_result["exp"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception:
                        exp_iso = gs1_result["exp"]

                raw_summary = (
                    f"Product: (GS1 Direct)\n"
                    f"Batch:   {gs1_result.get('batch') or ''}\n"
                    f"MFG:     {mfg_iso or ''}\n"
                    f"EXP:     {exp_iso or ''}"
                )
                ocr_data = {
                    "raw_text":         raw_summary,
                    "confidence":        1.0,
                    "line_count":        0,
                    "image_path":        image_path,
                    "expiry_date":       exp_iso,
                    "best_before_date":  exp_iso,
                    "batch_number":      gs1_result.get("batch"),
                    "price":             None,
                    "detected_fields": {
                        "mfg_date":     mfg_iso,
                        "lot_number":   None,
                        "weight":       None,
                        "product_name": None,
                    }
                }
            elif image_path and os.path.isfile(image_path):

                # ── STAGE 4A: Local PaddleOCR ─────────────────────────────────
                log.info("[Pipeline] Stage 4A: Running local PaddleOCR...")
                print("[Pipeline] Stage 4A: Running local PaddleOCR...", flush=True)
                local_ocr = None
                try:
                    local_ocr = extract_text(image_path)
                    log.info("[Pipeline] Stage 4A: PaddleOCR done. lines=%s conf=%.2f",
                             local_ocr.get("line_count", 0), local_ocr.get("confidence", 0))
                    print(f"[Pipeline] Stage 4A OK: lines={local_ocr.get('line_count',0)} "
                          f"conf={local_ocr.get('confidence', 0):.2f}", flush=True)
                except Exception as paddle_exc:
                    log.warning("[Pipeline] Stage 4A: PaddleOCR failed: %s", paddle_exc)
                    print(f"[Pipeline] Stage 4A WARN: PaddleOCR failed: {paddle_exc}", flush=True)

                # ── STAGE 4B: Text LLM (PaddleOCR text → structured JSON) ─────
                # Uses ~100 tokens per call — much cheaper than Vision LLM
                llm_text_result = None
                if local_ocr and local_ocr.get("raw_text"):
                    log.info("[Pipeline] Stage 4B: Sending OCR text to text LLM...")
                    print("[Pipeline] Stage 4B: Sending OCR text to text LLM...", flush=True)
                    llm_text_result = extract_structured_fields_from_text(local_ocr["raw_text"])
                    if llm_text_result:
                        log.info("[Pipeline] Stage 4B OK: expiry=%s mfg=%s conf=%.2f",
                                 llm_text_result.expiry_date, llm_text_result.mfg_date,
                                 llm_text_result.confidence_score)
                        print(f"[Pipeline] Stage 4B OK: expiry={llm_text_result.expiry_date} "
                              f"mfg={llm_text_result.mfg_date}", flush=True)
                    else:
                        log.info("[Pipeline] Stage 4B: Text LLM returned None (no API key or error).")
                        print("[Pipeline] Stage 4B: Text LLM skipped.", flush=True)

                # ── STAGE 4C: Vision LLM (Targeted ROI Crop / Full Image Fallback) ──
                # Triggered only when: (a) PaddleOCR found no text, OR
                #                      (b) text LLM could not parse dates
                llm_vision_result = None
                dates_missing = (
                    llm_text_result is None
                    or (not llm_text_result.expiry_date and not llm_text_result.mfg_date)
                )
                if dates_missing:
                    log.info("[Pipeline] Stage 4C: Dates missing — attempting targeted ROI Vision LLM...")
                    print("[Pipeline] Stage 4C: Dates missing — attempting targeted ROI Vision LLM...", flush=True)

                    # 1. Try to extract ROI crop from frame
                    crop_bytes, found = None, False
                    if frame is not None:
                        try:
                            from app.services.date_roi_service import extract_date_crop, crop_to_base64
                            crop_bytes, found = extract_date_crop(frame, barcode=barcode_raw)
                        except Exception as crop_exc:
                            log.warning("[Pipeline] ROI detection failed: %s", crop_exc)
                            print(f"[Pipeline] ROI crop failed: {crop_exc}", flush=True)

                    # 2. If ROI crop is found, query Vision LLM with is_crop=True
                    if found and crop_bytes:
                        try:
                            log.info("[Pipeline] Date ROI found. Sending crop to Vision LLM...")
                            print("[Pipeline] Date ROI found. Sending crop to Vision LLM...", flush=True)
                            crop_b64 = crop_to_base64(crop_bytes)
                            llm_vision_result = extract_structured_fields_via_llm(image_b64=crop_b64, is_crop=True)
                        except Exception as llm_crop_exc:
                            log.warning("[Pipeline] Vision LLM on ROI crop failed: %s", llm_crop_exc)
                            print(f"[Pipeline] Vision LLM on crop failed: {llm_crop_exc}", flush=True)

                    # 3. Fallback: No ROI found, or crop vision call failed -> Send full image with is_crop=False
                    if not llm_vision_result:
                        log.info("[Pipeline] ROI unavailable or failed. Sending full image to Vision LLM...")
                        print("[Pipeline] ROI unavailable or failed. Sending full image to Vision LLM...", flush=True)
                        try:
                            llm_vision_result = extract_structured_fields_via_llm(image_path=image_path, is_crop=False)
                        except Exception as llm_full_exc:
                            log.warning("[Pipeline] Vision LLM on full image failed: %s", llm_full_exc)
                            print(f"[Pipeline] Vision LLM on full image failed: {llm_full_exc}", flush=True)

                    if llm_vision_result:
                        log.info("[Pipeline] Stage 4C OK: expiry=%s mfg=%s conf=%.2f",
                                 llm_vision_result.expiry_date, llm_vision_result.mfg_date,
                                 llm_vision_result.confidence_score)
                        print(f"[Pipeline] Stage 4C OK: expiry={llm_vision_result.expiry_date} "
                              f"mfg={llm_vision_result.mfg_date}", flush=True)
                    else:
                        log.warning("[Pipeline] Stage 4C: Vision LLM also returned None.")
                        print("[Pipeline] Stage 4C: Vision LLM skipped.", flush=True)

                # ── Resolve best result ──────────────────────────────────────
                # Priority: Vision LLM (most accurate) > Text LLM > Raw Regex Heuristics
                final = llm_vision_result or llm_text_result

                if final:
                    raw_summary = (
                        f"Product: {final.product_name or ''}\n"
                        f"Batch:   {final.batch_number or ''}\n"
                        f"MFG:     {final.mfg_date or ''}\n"
                        f"EXP:     {final.expiry_date or ''}\n"
                        f"MRP:     {final.mrp or ''}\n"
                        f"Weight:  {final.weight or ''}"
                    )
                    # Merge partial GS1 batch/gtin if not already present
                    batch_val = final.batch_number
                    if not batch_val and partial_gs1:
                        batch_val = partial_gs1.get("batch")

                    # Handle relative shelf-life calculation for LLM outputs
                    exp_val = final.expiry_date
                    computed_flag = False
                    if final.mfg_date and not exp_val and getattr(final, "shelf_life_days", None):
                        try:
                            from dateutil.relativedelta import relativedelta
                            mfg_dt = datetime.strptime(final.mfg_date, "%Y-%m-%d").date()
                            exp_dt = mfg_dt + relativedelta(days=int(final.shelf_life_days))
                            exp_val = exp_dt.strftime("%Y-%m-%d")
                            computed_flag = True
                            log.info("[Pipeline] Computed expiry date %s from mfg %s using LLM shelf_life_days (%d days)",
                                     exp_val, final.mfg_date, final.shelf_life_days)
                        except Exception as math_exc:
                            log.warning("[Pipeline] Python relative date math failed: %s", math_exc)

                    ocr_data = {
                        "raw_text":         local_ocr["raw_text"] if local_ocr else raw_summary,
                        "confidence":        final.confidence_score,
                        "line_count":        local_ocr.get("line_count", 6) if local_ocr else 6,
                        "image_path":        image_path,
                        "expiry_date":       exp_val,
                        "best_before_date":  exp_val,
                        "batch_number":      batch_val,
                        "price":             final.mrp,
                        "exp_computed":      computed_flag,
                        "detected_fields": {
                            "mfg_date":     final.mfg_date,
                            "lot_number":   None,
                            "weight":       final.weight,
                            "product_name": final.product_name,
                        }
                    }
                    log.info("[Pipeline] Stage 4 COMPLETE via LLM: expiry=%s, computed=%s", exp_val, computed_flag)
                    print(f"[Pipeline] Stage 4 COMPLETE via LLM: expiry={exp_val} (computed={computed_flag})", flush=True)

                else:
                    # Final fallback: use raw regex heuristics on PaddleOCR text
                    log.info("[Pipeline] Stage 4 FINAL FALLBACK: running regex heuristics...")
                    print("[Pipeline] Stage 4 FINAL FALLBACK: regex heuristics.", flush=True)
                    if local_ocr and local_ocr.get("raw_text"):
                        extracted = extract_fields(local_ocr["raw_text"])

                        batch_val = extracted.candidate_batch
                        if not batch_val and partial_gs1:
                            batch_val = partial_gs1.get("batch")

                        ocr_data = {
                            **local_ocr,
                            "expiry_date":      extracted.candidate_expiry_date,
                            "best_before_date": extracted.candidate_best_before or extracted.candidate_expiry_date,
                            "batch_number":     batch_val,
                            "price":            extracted.candidate_mrp,
                            "exp_computed":      extracted.exp_computed,
                            "detected_fields": {
                                "mfg_date":   extracted.candidate_mfg_date,
                                "lot_number": extracted.candidate_lot,
                            }
                        }
                        log.info("[Pipeline] Regex heuristics OK: expiry=%s, computed=%s",
                                 extracted.candidate_expiry_date, extracted.exp_computed)
                        print(f"[Pipeline] Regex heuristics OK: expiry={extracted.candidate_expiry_date} "
                              f"(computed={extracted.exp_computed})", flush=True)
                    else:
                        log.warning("[Pipeline] No text and no LLM result. OCR data is empty.")
                        print("[Pipeline] No OCR data available.", flush=True)
            else:
                log.warning("[Pipeline] OCR skipped: image_path unavailable or file missing.")
                print("[Pipeline] OCR skipped: no valid image path.", flush=True)
        except Exception as exc:
            log.error("[Pipeline] OCR/Date Extraction FAILED: %s", exc, exc_info=True)
            print(f"[Pipeline] ERROR OCR/Date Extraction: {exc}", flush=True)
        execution_times["ocr_extraction"] = time.time() - t0

        # Cleanup temp file AFTER OCR completes (never before)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                log.info("[Pipeline] Temp file removed: %s", temp_file_path)
                print("[Pipeline] Temp file cleaned up.", flush=True)
            except Exception as exc:
                log.warning("[Pipeline] Could not remove temp file %s: %s", temp_file_path, exc)

        # ── Stage 5: Product Intelligence ───────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 5: Product Intelligence ---")
        print("[Pipeline] --- Stage 5: Product Intelligence ---", flush=True)
        try:
            profile = self.product_intel_service.build_product_profile(
                barcode_data=barcode_data,
                product_lookup=product_lookup,
                ocr_data=ocr_data
            )
            log.info("[Pipeline] Product profile built OK.")
            print("[Pipeline] Product profile built OK.", flush=True)
        except Exception as exc:
            log.error("[Pipeline] Product Intelligence FAILED: %s", exc, exc_info=True)
            print(f"[Pipeline] ERROR Product Intelligence: {exc}. Using empty fallback.", flush=True)
            profile = self.product_intel_service.build_product_profile()
        execution_times["product_intelligence"] = time.time() - t0

        # ── Stage 6: Validation ──────────────────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 6: Validation ---")
        print("[Pipeline] --- Stage 6: Validation ---", flush=True)
        validation_res = None
        try:
            validation_res = self.validation_service.validate_product(profile)
            log.info("[Pipeline] Validation OK: status=%s score=%s",
                     getattr(validation_res, "overall_status", None),
                     getattr(validation_res, "overall_score", None))
            print(f"[Pipeline] Validation OK: status={getattr(validation_res, 'overall_status', None)}", flush=True)
        except Exception as exc:
            log.error("[Pipeline] Validation FAILED: %s", exc, exc_info=True)
            print(f"[Pipeline] ERROR Validation: {exc}", flush=True)
        execution_times["validation"] = time.time() - t0

        # ── Stage 7: Alert Engine ────────────────────────────────────────────
        t0 = time.time()
        log.info("[Pipeline] --- Stage 7: Alert Engine ---")
        print("[Pipeline] --- Stage 7: Alert Engine ---", flush=True)
        alerts_res = None
        try:
            if validation_res:
                alerts_res = self.alert_service.generate_alerts(validation_res)
                alert_count = len(alerts_res.alerts) if alerts_res and alerts_res.alerts else 0
                log.info("[Pipeline] Alert Engine OK: %d alerts.", alert_count)
                print(f"[Pipeline] Alert Engine OK: {alert_count} alerts.", flush=True)
            else:
                log.info("[Pipeline] Alert Engine skipped (no validation result).")
                print("[Pipeline] Alert Engine skipped (no validation result).", flush=True)
        except Exception as exc:
            log.error("[Pipeline] Alert Engine FAILED: %s", exc, exc_info=True)
            print(f"[Pipeline] ERROR Alert Engine: {exc}", flush=True)
        execution_times["alert_generation"] = time.time() - t0

        # ── Final Result ─────────────────────────────────────────────────────
        total_time = time.time() - start_total

        status = "FAILED"
        if validation_res:
            if validation_res.overall_status == "VALID":
                status = "SUCCESS"
            elif validation_res.overall_status == "WARNING":
                status = "PARTIAL_SUCCESS"

        # Apply user confidence and missing expiry gate
        confidence = 0.0
        computed_flag = False
        if ocr_data:
            confidence = ocr_data.get("confidence", 0.0)
            computed_flag = bool(ocr_data.get("exp_computed", False))

        has_expiry = False
        if profile and profile.expiry and profile.expiry.expiry_date:
            has_expiry = True

        if confidence < 0.70 or not has_expiry:
            log.warning("[Pipeline] Scan rejected: confidence %.2f < 70%% or expiry_date missing.", confidence)
            status = "FAILED"

        result = PipelineResult(
            **profile.model_dump(),
            validation=validation_res,
            alerts=alerts_res,
            status=status,
            execution_times=execution_times,
            total_time=total_time,
            exp_computed=computed_flag
        )

        log.info("[Pipeline] === COMPLETE: status=%s, total_time=%.2fs, computed=%s ===", status, total_time, computed_flag)
        print(f"[Pipeline] === COMPLETE: status={status}, time={total_time:.2f}s, computed={computed_flag} ===", flush=True)
        return result
