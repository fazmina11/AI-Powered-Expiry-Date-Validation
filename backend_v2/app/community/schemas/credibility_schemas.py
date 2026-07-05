"""
community/schemas/credibility_schemas.py
Pydantic schemas for the Credibility Engine responses.
"""
import uuid
from typing import Dict
from pydantic import BaseModel, ConfigDict


class CredibilityFactors(BaseModel):
    barcode_verified: bool
    batch_verified: bool
    verified_user: bool
    images_uploaded: int
    receipt_uploaded: bool
    location_available: bool


class CredibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_id: uuid.UUID
    score: int
    credibility_level: str
    factors: CredibilityFactors


class CredibilitySummary(BaseModel):
    average_credibility: float
    highest_score: int
    lowest_score: int
    distribution_by_level: Dict[str, int]
