from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str


class DashboardSummaryResponse(BaseModel):
    total: int
    accepted: int
    priority_sale: int
    rejected: int
    manual_review: int
    invalid_date: int
