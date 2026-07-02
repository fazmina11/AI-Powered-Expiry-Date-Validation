from pydantic import BaseModel, Field
from typing import List, Optional

class AlertSeverity:
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

class AlertCode:
    BARCODE_INVALID = "BARCODE_INVALID"
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    MFG_NOT_FOUND = "MFG_NOT_FOUND"
    INVALID_DATE_SEQUENCE = "INVALID_DATE_SEQUENCE"
    EXPIRY_NOT_FOUND = "EXPIRY_NOT_FOUND"
    MRP_NOT_FOUND = "MRP_NOT_FOUND"
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"

class Alert(BaseModel):
    code: str
    severity: str
    message: str
    recommended_action: str

class AlertResult(BaseModel):
    alerts: List[Alert] = Field(default_factory=list)
    total_alerts: int = 0
    highest_severity: Optional[str] = None
