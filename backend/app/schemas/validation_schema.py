"""
schemas/validation_schema.py — Pydantic schemas for ValidationRecord management.

ValidationCreate   — POST /validation/manual  request body
ValidationResponse — response shape for a stored ValidationRecord

The OCR team will POST to /validation/manual with raw_text and
extracted dates. confidence_score drives the validation_status logic.
No OCR logic lives here — this is purely a data contract.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ValidationCreate(BaseModel):
    """
    Payload for POST /validation/manual.

    Designed so the future OCR pipeline can push results directly:
      - raw_text:            raw string extracted from the label image
      - extracted_mfg_date:  parsed manufacturing date
      - extracted_expiry_date: parsed expiry date
      - confidence_score:    model confidence 0.0–1.0 (None = manual entry)
    """
    inventory_item_id:     int
    raw_text:              Optional[str]   = None
    extracted_mfg_date:    Optional[date]  = None
    extracted_expiry_date: Optional[date]  = None
    confidence_score:      Optional[float] = None

    @field_validator("confidence_score")
    @classmethod
    def score_must_be_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        return v


class ValidationResponse(BaseModel):
    """Full shape of a ValidationRecord returned to the client."""
    id:                    int
    inventory_item_id:     int
    raw_text:              Optional[str]
    extracted_mfg_date:    Optional[date]
    extracted_expiry_date: Optional[date]
    confidence_score:      Optional[float]
    validation_status:     str
    failure_reason:        Optional[str]
    created_at:            datetime

    model_config = ConfigDict(from_attributes=True)
