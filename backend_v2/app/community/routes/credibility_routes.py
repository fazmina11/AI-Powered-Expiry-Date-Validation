"""
community/routes/credibility_routes.py
HTTP routes for PGN Consumer Report Credibility Engine (CRCE).
"""
import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.credibility_schemas import CredibilityResponse, CredibilitySummary
from app.community.services import credibility_service
from app.community.models.product_report import ProductReport

router = APIRouter(tags=["Consumer Report Credibility Engine"])


def _map_to_response(cred) -> dict:
    """Helper to convert flat database fields to nested Pydantic response shape."""
    return {
        "report_id": cred.report_id,
        "score": cred.score,
        "credibility_level": cred.credibility_level,
        "factors": {
            "barcode_verified": cred.barcode_verified,
            "batch_verified": cred.batch_verified,
            "verified_user": cred.verified_user,
            "images_uploaded": cred.images_uploaded,
            "receipt_uploaded": cred.receipt_uploaded,
            "location_available": cred.location_available,
        }
    }


@router.get(
    "/reports/{report_id}/credibility",
    response_model=CredibilityResponse,
    summary="Get report credibility details",
    responses={404: {"description": "Report not found"}},
)
def get_report_credibility(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve the calculated credibility score and factors analysis for a report.
    If the score hasn't been computed yet, it calculates and saves it automatically.
    """
    # Verify report exists
    exists = db.query(ProductReport.id).filter(ProductReport.id == report_id).scalar() is not None
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "REPORT_NOT_FOUND",
                "message": f"Product report '{report_id}' not found.",
            },
        )
    
    cred = credibility_service.get_report_score(db, report_id)
    return _map_to_response(cred)


@router.post(
    "/reports/{report_id}/recalculate",
    response_model=CredibilityResponse,
    summary="Manually trigger report credibility recalculation",
    responses={404: {"description": "Report not found"}},
)
def recalculate_report_credibility(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Manually force the recalculation of credibility rules for a report.
    Normally done automatically when data changes, but available for sync/audit.
    """
    # Verify report exists
    exists = db.query(ProductReport.id).filter(ProductReport.id == report_id).scalar() is not None
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "REPORT_NOT_FOUND",
                "message": f"Product report '{report_id}' not found.",
            },
        )

    cred = credibility_service.recalculate_report(db, report_id)
    return _map_to_response(cred)


@router.get(
    "/credibility/statistics",
    response_model=CredibilitySummary,
    summary="Get community reporting credibility summary statistics",
)
def get_credibility_statistics(
    db: Session = Depends(get_db),
):
    """
    Generate aggregate statistics on consumer reporting reliability:
    - Average score
    - Range of scores (highest & lowest)
    - Count breakdown by level (VERY_HIGH, HIGH, MEDIUM, LOW, VERY_LOW)
    """
    return credibility_service.get_statistics(db)
