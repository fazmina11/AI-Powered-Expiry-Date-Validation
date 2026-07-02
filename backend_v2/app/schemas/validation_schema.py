from pydantic import BaseModel
from typing import Optional

class ValidationStatus:
    VALID = "VALID"
    WARNING = "WARNING"
    ERROR = "ERROR"

class CategoryValidation(BaseModel):
    status: str
    score: int
    message: str

class ValidationResult(BaseModel):
    overall_score: int
    overall_status: str
    barcode: CategoryValidation
    product: CategoryValidation
    manufacturing: CategoryValidation
    expiry: CategoryValidation
    pricing: CategoryValidation
    ocr: CategoryValidation
