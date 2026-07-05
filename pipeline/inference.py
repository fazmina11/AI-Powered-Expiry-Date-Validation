import os
import cv2
from datetime import datetime
from pipeline.detector import detect_date_region, crop_date_regions
from pipeline.ocr_engine import try_all_preprocessings
from pipeline.date_parser import parse_date

def calculate_status(parsed_date, near_expiry_days):
    if not parsed_date:
        return "undetected", None
    
    today = datetime.now()
    try:
        expiry_dt = datetime.strptime(parsed_date, "%Y-%m-%d")
        days_remaining = (expiry_dt - today).days
        
        if days_remaining < 0:
            return "expired", days_remaining
        elif days_remaining <= near_expiry_days:
            return "near_expiry", days_remaining
        else:
            return "valid", days_remaining
    except ValueError:
        return "undetected", None

def run_pipeline(image_path, near_expiry_threshold_days=30):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Invalid image path: {image_path}")
            
        # 1. Detect date region
        boxes = detect_date_region(image)
        detection_used = len(boxes) > 0
        
        best_ocr_result = None
        best_date = None
        best_confidence = 0.0
        best_extraction_method = "none"
        raw_text = ""
        raw_match = ""
        detection_conf = 0.0
        
        if detection_used:
            # Get best detection confidence
            detection_conf = max([box[4] for box in boxes])
            crops = crop_date_regions(image, boxes)
            
            for crop in crops:
                ocr_result, conf = try_all_preprocessings(crop)
                parsed, match, method = parse_date(ocr_result)
                if parsed and conf > best_confidence:
                    best_date = parsed
                    best_confidence = conf
                    best_extraction_method = method
                    raw_text = ocr_result
                    raw_match = match
                    
        # Always evaluate the full image as a safety candidate. YOLO crops are
        # faster and often cleaner, but full-frame OCR preserves context when a
        # box is slightly clipped or the detector chooses nearby label text.
        ocr_result, conf = try_all_preprocessings(image)
        parsed, match, method = parse_date(ocr_result)
        if parsed and (not best_date or conf >= best_confidence * 0.90):
            best_date = parsed
            best_confidence = conf
            best_extraction_method = method
            raw_text = ocr_result
            raw_match = match
        elif not best_date and conf > best_confidence:
            best_confidence = conf
            raw_text = ocr_result

        status, days_rem = calculate_status(best_date, near_expiry_threshold_days)
        
        review_required = False
        review_reason = ""
        
        if best_confidence < 0.65:
            status = "manual_review_required"
            review_reason = "Low OCR confidence"
        elif best_extraction_method == "none":
            status = "manual_review_required"
            review_reason = "No date pattern found"
            
        result = {
            "status": status,
            "expiry_date": best_date,
            "days_remaining": days_rem,
            "raw_ocr_text": raw_text,
            "raw_date_match": raw_match,
            "extraction_method": best_extraction_method,
            "ocr_confidence": float(best_confidence),
            "detection_confidence": float(detection_conf),
            "detection_used": detection_used,
            "near_expiry_threshold_days": near_expiry_threshold_days
        }
        
        if status == "manual_review_required":
            result["review_reason"] = review_reason
            
        return result

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }
