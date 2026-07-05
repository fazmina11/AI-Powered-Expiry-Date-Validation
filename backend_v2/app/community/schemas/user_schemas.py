"""
community/schemas/user_schemas.py
Pydantic v2 schemas for CommunityUser.
"""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


_PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")


class CommunityUserCreate(BaseModel):
    """Payload to create a new community user."""

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not _PHONE_RE.match(cleaned):
            raise ValueError(
                "Phone must be 7–15 digits, optionally starting with '+'. "
                "Example: +919876543210"
            )
        return cleaned


class CommunityUserUpdate(BaseModel):
    """Partial update — all fields optional."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not _PHONE_RE.match(cleaned):
            raise ValueError("Phone must be 7–15 digits, optionally starting with '+'.")
        return cleaned


class CommunityUserResponse(BaseModel):
    """API response shape for a community user."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    phone: Optional[str]
    is_verified: bool
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    created_at: datetime
    updated_at: datetime
