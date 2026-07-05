"""
community/services/report_service.py
All business logic for product reports and report images.
No SQL inside routes — everything here.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.community.models.community_user import CommunityUser
from app.community.models.product_report  import ProductReport
from app.community.models.report_image    import ReportImage
from app.community.schemas.report_schemas import (
    ProductReportCreate,
    ProductReportUpdate,
    ReportImageCreate,
)
from app.community.enums import ReportStatus

_MAX_IMAGES = 5
_DEDUP_WINDOW_HOURS = 24


def _assert_user_exists(db: Session, user_id: uuid.UUID) -> None:
    """Raises 404 if the community user does not exist."""
    exists = db.query(CommunityUser.id).filter(CommunityUser.id == user_id).scalar()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "USER_NOT_FOUND",
                "message": f"Community user '{user_id}' not found.",
            },
        )


def _check_duplicate(
    db: Session,
    user_id: uuid.UUID,
    barcode: str,
    batch_number: str,
    report_type,
) -> None:
    """
    Reject duplicate reports: same user + barcode + batch + type within 24 hours.
    Raises 409 if a duplicate is found.
    """
    window_start = datetime.now(timezone.utc) - timedelta(hours=_DEDUP_WINDOW_HOURS)
    duplicate = (
        db.query(ProductReport)
        .filter(
            ProductReport.user_id     == user_id,
            ProductReport.barcode     == barcode,
            ProductReport.batch_number == batch_number,
            ProductReport.report_type == report_type,
            ProductReport.created_at  >= window_start,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_REPORT",
                "message": (
                    "A report for the same barcode, batch number, and report type "
                    "was already submitted by this user within the last 24 hours."
                ),
                "existing_report_id": str(duplicate.id),
            },
        )


def create_report(db: Session, payload: ProductReportCreate) -> ProductReport:
    """
    Create a new product report with optional inline images.
    Enforces: user existence, duplicate check, max 5 images.
    """
    _assert_user_exists(db, payload.user_id)
    _check_duplicate(
        db, payload.user_id, payload.barcode,
        payload.batch_number, payload.report_type
    )

    report = ProductReport(
        user_id=payload.user_id,
        barcode=payload.barcode,
        batch_number=payload.batch_number,
        product_name=payload.product_name,
        report_type=payload.report_type,
        severity=payload.severity,
        description=payload.description,
        purchase_location=payload.purchase_location,
        purchase_date=payload.purchase_date,
        status=ReportStatus.PENDING,
    )
    db.add(report)
    db.flush()  # get report.id before inserting images

    if payload.images:
        for img in payload.images:
            db.add(ReportImage(report_id=report.id, image_url=img.image_url))

    db.commit()
    
    # Automatically calculate credibility score for the new report
    from app.community.services.credibility_service import recalculate_report
    recalculate_report(db, report.id)
    
    # Automatically associate the report with an issue cluster
    from app.community.services.issue_cluster_service import find_matching_cluster, create_cluster, add_report_to_cluster
    cluster = find_matching_cluster(db, report)
    if not cluster:
        cluster = create_cluster(db, report)
    add_report_to_cluster(db, cluster.id, report.id)
    
    db.refresh(report)
    return report


def get_report(db: Session, report_id: uuid.UUID) -> ProductReport:
    """Fetch a single report by ID. Raises 404 if not found."""
    report = (
        db.query(ProductReport)
        .filter(ProductReport.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "REPORT_NOT_FOUND",
                "message": f"Product report '{report_id}' not found.",
            },
        )
    return report


def list_reports(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[ReportStatus] = None,
) -> List[ProductReport]:
    """List reports with optional status filter and pagination."""
    q = db.query(ProductReport)
    if status_filter:
        q = q.filter(ProductReport.status == status_filter)
    return q.order_by(ProductReport.created_at.desc()).offset(skip).limit(limit).all()


def get_reports_by_barcode(
    db: Session, barcode: str, skip: int = 0, limit: int = 20
) -> List[ProductReport]:
    """Return all reports for a specific product barcode."""
    return (
        db.query(ProductReport)
        .filter(ProductReport.barcode == barcode)
        .order_by(ProductReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_report(
    db: Session, report_id: uuid.UUID, payload: ProductReportUpdate
) -> ProductReport:
    """Partial update — for status transitions or description edits."""
    report = get_report(db, report_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    db.commit()
    
    # Automatically recalculate credibility score on report updates
    from app.community.services.credibility_service import recalculate_report
    recalculate_report(db, report.id)
    
    # Recalculate cluster intelligence if the report belongs to a cluster
    from app.community.models.issue_cluster import ClusterReport
    link = db.query(ClusterReport).filter(ClusterReport.report_id == report.id).first()
    if link:
        from app.community.services.community_intelligence_service import recalculate_cluster
        recalculate_cluster(db, link.cluster_id)
    
    db.refresh(report)
    return report


def upload_report_image(
    db: Session, report_id: uuid.UUID, payload: ReportImageCreate
) -> ReportImage:
    """
    Attach one image URL to an existing report.
    Enforces the 5-image maximum.
    Raises 404 if report not found, 400 if limit exceeded.
    """
    report = get_report(db, report_id)

    current_count = (
        db.query(ReportImage)
        .filter(ReportImage.report_id == report_id)
        .count()
    )
    if current_count >= _MAX_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "IMAGE_LIMIT_EXCEEDED",
                "message": f"A report can have at most {_MAX_IMAGES} images. "
                           f"This report already has {current_count}.",
            },
        )

    image = ReportImage(report_id=report.id, image_url=payload.image_url)
    db.add(image)
    db.commit()
    
    # Automatically recalculate credibility score when a new image is added
    from app.community.services.credibility_service import recalculate_report
    recalculate_report(db, report_id)
    
    # Recalculate cluster intelligence if the report belongs to a cluster
    from app.community.models.issue_cluster import ClusterReport
    link = db.query(ClusterReport).filter(ClusterReport.report_id == report_id).first()
    if link:
        from app.community.services.community_intelligence_service import recalculate_cluster
        recalculate_cluster(db, link.cluster_id)
    
    db.refresh(image)
    return image
