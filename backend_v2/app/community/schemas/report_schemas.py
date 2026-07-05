"""
community/schemas/report_schemas.py
Pydantic v2 schemas for ProductReport and ReportImage.
"""
import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.community.enums import ReportType, ReportStatus, Severity


class ReportImageCreate(BaseModel):
    """Payload to attach an image URL to a report."""
    image_url: str = Field(..., min_length=10, max_length=2048)

    @field_validator("image_url")
    @classmethod
    def must_be_url(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("image_url must be a valid http/https URL.")
        return v


class ReportImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_id: uuid.UUID
    image_url: str
    uploaded_at: datetime


# ── Product Report ────────────────────────────────────────────────────────────

class ProductReportCreate(BaseModel):
    """Payload to create a new product report."""

    user_id: uuid.UUID
    barcode: str = Field(..., min_length=1, max_length=100)
    batch_number: str = Field(..., min_length=1, max_length=100)
    product_name: Optional[str] = Field(None, max_length=255)
    report_type: ReportType
    severity: Severity
    description: str = Field(..., min_length=20, max_length=5000)
    purchase_location: Optional[str] = Field(None, max_length=255)
    purchase_date: Optional[date] = None
    images: Optional[List[ReportImageCreate]] = Field(default=None, max_length=5)

    @field_validator("barcode")
    @classmethod
    def barcode_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("barcode cannot be blank.")
        return v.strip()

    @field_validator("batch_number")
    @classmethod
    def batch_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("batch_number cannot be blank.")
        return v.strip()

    @field_validator("purchase_date")
    @classmethod
    def purchase_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("purchase_date cannot be a future date.")
        return v

    @field_validator("images")
    @classmethod
    def max_five_images(cls, v: Optional[list]) -> Optional[list]:
        if v and len(v) > 5:
            raise ValueError("A report cannot have more than 5 images.")
        return v


class ProductReportUpdate(BaseModel):
    """Partial update for a report — status changes by reviewers."""
    status: Optional[ReportStatus] = None
    description: Optional[str] = Field(None, min_length=20, max_length=5000)


class ProductReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    barcode: str
    batch_number: str
    product_name: Optional[str]
    report_type: ReportType
    severity: Severity
    description: str
    purchase_location: Optional[str]
    purchase_date: Optional[date]
    status: ReportStatus
    created_at: datetime
    updated_at: datetime
    images: List[ReportImageResponse] = []
