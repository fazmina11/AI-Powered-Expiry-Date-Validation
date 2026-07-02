from app.schemas.alert_schema import AlertResult, Alert, AlertCode, AlertSeverity
from app.schemas.validation_schema import ValidationResult, ValidationStatus

class AlertService:
    def generate_alerts(self, validation_result: ValidationResult) -> AlertResult:
        alerts = []
        
        if not validation_result:
            return AlertResult(alerts=[], total_alerts=0, highest_severity=None)

        try:
            # 1. BARCODE_INVALID
            if validation_result.barcode.status == ValidationStatus.ERROR:
                alerts.append(Alert(
                    code=AlertCode.BARCODE_INVALID,
                    severity=AlertSeverity.CRITICAL,
                    message="Barcode is missing or invalid.",
                    recommended_action="Rescan the barcode."
                ))

            # 2. PRODUCT_NOT_FOUND
            if validation_result.product.status == ValidationStatus.ERROR:
                alerts.append(Alert(
                    code=AlertCode.PRODUCT_NOT_FOUND,
                    severity=AlertSeverity.WARNING,
                    message="Product could not be found in local or external databases.",
                    recommended_action="Enter product details manually or try another barcode."
                ))

            # 3. MFG_NOT_FOUND
            if validation_result.manufacturing.status == ValidationStatus.WARNING and "missing" in validation_result.manufacturing.message.lower():
                alerts.append(Alert(
                    code=AlertCode.MFG_NOT_FOUND,
                    severity=AlertSeverity.INFO,
                    message="Manufacturing date was not detected.",
                    recommended_action="Manually verify the manufacturing date if needed."
                ))

            # 4. EXPIRY_NOT_FOUND & 5. INVALID_DATE_SEQUENCE
            if validation_result.expiry.status == ValidationStatus.ERROR:
                msg = validation_result.expiry.message.lower()
                if "after manufacturing" in msg:
                    alerts.append(Alert(
                        code=AlertCode.INVALID_DATE_SEQUENCE,
                        severity=AlertSeverity.CRITICAL,
                        message="Expiry date is before the manufacturing date.",
                        recommended_action="Check the extracted dates for errors or rescan the label."
                    ))
                else:
                    alerts.append(Alert(
                        code=AlertCode.EXPIRY_NOT_FOUND,
                        severity=AlertSeverity.CRITICAL,
                        message="Expiry date is missing or invalid.",
                        recommended_action="Rescan the expiry label or enter it manually."
                    ))

            # 6. MRP_NOT_FOUND
            if validation_result.pricing.status == ValidationStatus.WARNING and "missing" in validation_result.pricing.message.lower():
                alerts.append(Alert(
                    code=AlertCode.MRP_NOT_FOUND,
                    severity=AlertSeverity.INFO,
                    message="MRP (price) was not found.",
                    recommended_action="Enter the price manually if tracking is required."
                ))

            # 7. LOW_OCR_CONFIDENCE
            if validation_result.ocr.status in [ValidationStatus.WARNING, ValidationStatus.ERROR]:
                severity = AlertSeverity.CRITICAL if validation_result.ocr.status == ValidationStatus.ERROR else AlertSeverity.WARNING
                alerts.append(Alert(
                    code=AlertCode.LOW_OCR_CONFIDENCE,
                    severity=severity,
                    message="OCR extraction had low confidence or failed.",
                    recommended_action="Ensure the label is clear and well-lit, then rescan."
                ))

        except Exception:
            # Never raise exceptions
            pass
            
        # Compute highest severity
        highest_severity = None
        if alerts:
            severities = [a.severity for a in alerts]
            if AlertSeverity.CRITICAL in severities:
                highest_severity = AlertSeverity.CRITICAL
            elif AlertSeverity.WARNING in severities:
                highest_severity = AlertSeverity.WARNING
            else:
                highest_severity = AlertSeverity.INFO
                
        return AlertResult(
            alerts=alerts,
            total_alerts=len(alerts),
            highest_severity=highest_severity
        )


def log_audit_event(
    db,
    event_type: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = "system",
    actor_type: str | None = "system",
    before_state: dict | None = None,
    after_state: dict | None = None,
    change_summary: str | None = None,
):
    """Log a significant system action to the audit_logs table."""
    from app.models.audit_log import AuditLog
    try:
        log_entry = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_type=actor_type,
            before_state=before_state,
            after_state=after_state,
            change_summary=change_summary,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).warning(f"[AuditLog] Failed to write event {event_type}: {e}")
        return None


def process_ocr_result(ocr_result: dict) -> dict:
    """
    Shim function for Sprint 4 & dev_tools compatibility.
    Processes raw OCR text, runs date extraction, generates alerts, and returns the expected nested dict.
    """
    from app.services.date_extraction_service import extract_fields
    
    raw_text = ocr_result.get("raw_text", "")
    confidence = ocr_result.get("confidence", 0.0)
    
    # Extract fields using Standalone Date Extractor under the hood
    extracted = extract_fields(raw_text).to_dict()
    
    # Generate mock validation result for alert service
    from app.schemas.validation_schema import ValidationResult, CategoryValidation, ValidationStatus
    from app.schemas.alert_schema import Alert
    
    # Let's map validation status based on presence of fields
    mfg_status = ValidationStatus.VALID if extracted.get("candidate_mfg_date") else ValidationStatus.WARNING
    exp_status = ValidationStatus.VALID if extracted.get("candidate_expiry_date") else ValidationStatus.ERROR
    ocr_status = ValidationStatus.VALID if confidence >= 0.8 else (ValidationStatus.WARNING if confidence >= 0.6 else ValidationStatus.ERROR)
    
    val_res = ValidationResult(
        overall_score=100,
        overall_status=ValidationStatus.VALID,
        barcode=CategoryValidation(status=ValidationStatus.VALID, score=100, message="OK"),
        product=CategoryValidation(status=ValidationStatus.VALID, score=100, message="OK"),
        manufacturing=CategoryValidation(status=mfg_status, score=100 if mfg_status == ValidationStatus.VALID else 50, message="Mfg Date"),
        expiry=CategoryValidation(status=exp_status, score=100 if exp_status == ValidationStatus.VALID else 0, message="Expiry Date"),
        pricing=CategoryValidation(status=ValidationStatus.VALID, score=100, message="OK"),
        ocr=CategoryValidation(status=ocr_status, score=int(confidence*100), message="OCR")
    )
    
    # Generate alerts using our service
    from app.services.alert_service import AlertService
    alerts_obj = AlertService().generate_alerts(val_res)
    
    # Format alerts for the test framework which expects list of {"code": ..., "detail": ...}
    formatted_alerts = []
    for a in alerts_obj.alerts:
        formatted_alerts.append({
            "code": a.code,
            "detail": a.message
        })
        
    # Build nested result dict expected by test_extraction.py
    def make_val(val):
        return {"value": val} if val else None
        
    all_dates = []
    if extracted.get("candidate_mfg_date"): all_dates.append(extracted["candidate_mfg_date"])
    if extracted.get("candidate_expiry_date"): all_dates.append(extracted["candidate_expiry_date"])
    if extracted.get("candidate_pkd_date"): all_dates.append(extracted["candidate_pkd_date"])
    if extracted.get("candidate_best_before"): all_dates.append(extracted["candidate_best_before"])
        
    return {
        "manufacturing_information": {
            "mfg_date": make_val(extracted.get("candidate_mfg_date")),
            "pkd_date": make_val(extracted.get("candidate_pkd_date")),
            "batch": make_val(extracted.get("candidate_batch")),
            "lot": make_val(extracted.get("candidate_lot"))
        },
        "expiry_information": {
            "expiry_date": make_val(extracted.get("candidate_expiry_date")),
            "best_before": make_val(extracted.get("candidate_best_before"))
        },
        "pricing_information": {
            "mrp": make_val(extracted.get("candidate_mrp"))
        },
        "ocr_information": {
            "confidence": confidence,
            "all_dates_found": all_dates
        },
        "alerts": formatted_alerts
    }
