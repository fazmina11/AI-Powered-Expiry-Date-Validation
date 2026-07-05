"""
community/routes/report_routes.py
HTTP routes for /api/v1/community/reports
All business logic delegated to report_service.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.enums import ReportStatus
from app.community.schemas.report_schemas import (
    ProductReportCreate,
    ProductReportResponse,
    ProductReportUpdate,
    ReportImageCreate,
    ReportImageResponse,
)
from app.community import services as svc

router = APIRouter(prefix="/reports", tags=["Community Reports"])


@router.post(
    "",
    response_model=ProductReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a product report",
    responses={
        400: {"description": "Validation error (e.g. future date, >5 images)"},
        404: {"description": "User not found"},
        409: {"description": "Duplicate report within 24 hours"},
        422: {"description": "Request body schema error"},
    },
)
def create_report(
    payload: ProductReportCreate,
    db: Session = Depends(get_db),
) -> ProductReportResponse:
    """
    Submit a new product quality / safety report.

    **Business rules enforced:**
    - `user_id` must exist in community_users
    - `barcode` and `batch_number` are required
    - `description` must be at least 20 characters
    - `purchase_date` cannot be in the future
    - At most 5 inline images per report
    - Duplicate reports (same user + barcode + batch + type within 24 h) are rejected with **409**
    """
    return svc.report_service.create_report(db, payload)


@router.get(
    "",
    response_model=List[ProductReportResponse],
    summary="List product reports",
)
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
) -> List[ProductReportResponse]:
    """
    Paginated list of all reports.
    Optionally filter by `status` (PENDING | UNDER_REVIEW | VERIFIED | REJECTED).
    """
    return svc.report_service.list_reports(db, skip=skip, limit=limit, status_filter=status_filter)


@router.get(
    "/barcode/{barcode}",
    response_model=List[ProductReportResponse],
    summary="Get all reports for a specific barcode",
)
def get_reports_by_barcode(
    barcode: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[ProductReportResponse]:
    """Return all community reports filed against a specific product barcode."""
    return svc.report_service.get_reports_by_barcode(db, barcode, skip=skip, limit=limit)


@router.get(
    "/{report_id}",
    response_model=ProductReportResponse,
    summary="Get a single report by ID",
    responses={404: {"description": "Report not found"}},
)
def get_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ProductReportResponse:
    """Fetch a single product report including all attached images."""
    return svc.report_service.get_report(db, report_id)


@router.put(
    "/{report_id}",
    response_model=ProductReportResponse,
    summary="Update a report (status / description)",
    responses={404: {"description": "Report not found"}},
)
def update_report(
    report_id: uuid.UUID,
    payload: ProductReportUpdate,
    db: Session = Depends(get_db),
) -> ProductReportResponse:
    """Partially update a report's status or description."""
    return svc.report_service.update_report(db, report_id, payload)


@router.post(
    "/{report_id}/images",
    response_model=ReportImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach an image URL to a report",
    responses={
        400: {"description": "Image limit exceeded (max 5)"},
        404: {"description": "Report not found"},
    },
)
def upload_report_image(
    report_id: uuid.UUID,
    payload: ReportImageCreate,
    db: Session = Depends(get_db),
) -> ReportImageResponse:
    """
    Attach a single image URL to an existing report.
    Returns **400** when the report already has 5 images.
    """
    return svc.report_service.upload_report_image(db, report_id, payload)
