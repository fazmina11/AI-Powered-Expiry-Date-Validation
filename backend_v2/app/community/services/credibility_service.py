"""
community/services/credibility_service.py
Pure business logic for the Consumer Report Credibility Engine (CRCE).
No ML is used — calculation uses standard deterministic database attributes.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.community.models.community_user import CommunityUser
from app.community.models.product_report import ProductReport
from app.community.models.report_image   import ReportImage
from app.community.models.report_credibility import ReportCredibility


def calculate_description_score(description: str) -> int:
    """
    Calculate description length score:
    - 20-50 chars: +5
    - 51-150 chars: +10
    - More than 150 chars: +15
    """
    length = len(description)
    if 20 <= length <= 50:
        return 5
    elif 51 <= length <= 150:
        return 10
    elif length > 150:
        return 15
    return 0


def calculate_duplicate_penalty(
    db: Session,
    user_id: uuid.UUID,
    barcode: str,
    batch_number: str,
    report_type: str,
    report_id: Optional[uuid.UUID] = None,
) -> int:
    """
    Calculate duplicate penalty:
    -10 for each previous duplicate report (same user, barcode, batch, type).
    Maximum penalty is -30.
    """
    query = db.query(ProductReport).filter(
        ProductReport.user_id      == user_id,
        ProductReport.barcode      == barcode,
        ProductReport.batch_number == batch_number,
        ProductReport.report_type  == report_type,
    )
    if report_id:
        query = query.filter(ProductReport.id != report_id)

    dup_count = query.count()
    penalty = dup_count * 10
    return min(penalty, 30)


def calculate_credibility_level(score: int) -> str:
    """
    Determine credibility level based on score:
    - 90-100: VERY_HIGH
    - 75-89: HIGH
    - 50-74: MEDIUM
    - 25-49: LOW
    - 0-24: VERY_LOW
    """
    if score >= 90:
        return "VERY_HIGH"
    elif score >= 75:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    elif score >= 25:
        return "LOW"
    return "VERY_LOW"


def calculate_score(db: Session, report: ProductReport) -> Dict[str, Any]:
    """
    Evaluate credibility factors and calculate final score out of 100.
    """
    # 1. Barcode exists in master products (+20)
    barcode_exists = db.query(Product.id).filter(Product.barcode == report.barcode).scalar() is not None
    barcode_score = 20 if barcode_exists else 0

    # 2. Batch number provided (+15)
    batch_provided = bool(report.batch_number and report.batch_number.strip())
    batch_score = 15 if batch_provided else 0

    # 3. At least one image (+15)
    images_count = db.query(ReportImage).filter(ReportImage.report_id == report.id).count()
    images_score = 15 if images_count > 0 else 0

    # 4. Receipt uploaded (+15)
    # Check if any image url contains the keyword 'receipt' case-insensitively
    receipt_uploaded = db.query(ReportImage).filter(
        ReportImage.report_id == report.id,
        ReportImage.image_url.ilike("%receipt%")
    ).first() is not None
    receipt_score = 15 if receipt_uploaded else 0

    # 5. Verified community user (+10)
    user_verified = db.query(CommunityUser.is_verified).filter(CommunityUser.id == report.user_id).scalar() or False
    user_score = 10 if user_verified else 0

    # 6. Description length (+5, +10, or +15)
    desc_score = calculate_description_score(report.description or "")

    # 7. Purchase date valid (+10)
    # Date validation exists at the API border, presence here indicates validity.
    purchase_date_valid = report.purchase_date is not None
    date_score = 10 if purchase_date_valid else 0

    # 8. Location available (+5)
    location_available = bool(report.purchase_location and report.purchase_location.strip())
    location_score = 5 if location_available else 0

    # 9. Previous duplicate reports penalty (-10 each, max -30)
    duplicate_count = db.query(ProductReport).filter(
        ProductReport.user_id      == report.user_id,
        ProductReport.barcode      == report.barcode,
        ProductReport.batch_number == report.batch_number,
        ProductReport.report_type  == report.report_type,
        ProductReport.id           != report.id,
    ).count()
    penalty_score = min(duplicate_count * 10, 30)

    # Sum and clamp to [0, 100]
    total_score = (
        barcode_score +
        batch_score +
        images_score +
        receipt_score +
        user_score +
        desc_score +
        date_score +
        location_score -
        penalty_score
    )
    clamped_score = max(0, min(total_score, 100))
    cred_level = calculate_credibility_level(clamped_score)

    return {
        "barcode_verified": barcode_exists,
        "batch_verified": batch_provided,
        "images_uploaded": images_count,
        "receipt_uploaded": receipt_uploaded,
        "verified_user": user_verified,
        "description_length": len(report.description or ""),
        "duplicate_reports": duplicate_count,
        "location_available": location_available,
        "purchase_date_valid": purchase_date_valid,
        "score": clamped_score,
        "credibility_level": cred_level,
    }


def recalculate_report(db: Session, report_id: uuid.UUID) -> ReportCredibility:
    """
    Recalculate report credibility score and save it to the DB.
    """
    report = db.query(ProductReport).filter(ProductReport.id == report_id).first()
    if not report:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    factors = calculate_score(db, report)
    credibility = db.query(ReportCredibility).filter(ReportCredibility.report_id == report_id).first()

    if not credibility:
        credibility = ReportCredibility(
            report_id=report_id,
            barcode_verified=factors["barcode_verified"],
            batch_verified=factors["batch_verified"],
            images_uploaded=factors["images_uploaded"],
            receipt_uploaded=factors["receipt_uploaded"],
            verified_user=factors["verified_user"],
            description_length=factors["description_length"],
            duplicate_reports=factors["duplicate_reports"],
            location_available=factors["location_available"],
            purchase_date_valid=factors["purchase_date_valid"],
            score=factors["score"],
            credibility_level=factors["credibility_level"],
            calculated_at=datetime.now(timezone.utc),
        )
        db.add(credibility)
    else:
        credibility.barcode_verified = factors["barcode_verified"]
        credibility.batch_verified = factors["batch_verified"]
        credibility.images_uploaded = factors["images_uploaded"]
        credibility.receipt_uploaded = factors["receipt_uploaded"]
        credibility.verified_user = factors["verified_user"]
        credibility.description_length = factors["description_length"]
        credibility.duplicate_reports = factors["duplicate_reports"]
        credibility.location_available = factors["location_available"]
        credibility.purchase_date_valid = factors["purchase_date_valid"]
        credibility.score = factors["score"]
        credibility.credibility_level = factors["credibility_level"]
        credibility.calculated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(credibility)
    return credibility


def get_report_score(db: Session, report_id: uuid.UUID) -> ReportCredibility:
    """
    Get the credibility details of a report. If missing, calculate it on the fly.
    """
    credibility = db.query(ReportCredibility).filter(ReportCredibility.report_id == report_id).first()
    if not credibility:
        # Calculate on the fly if missing
        credibility = recalculate_report(db, report_id)
    return credibility


def get_statistics(db: Session) -> Dict[str, Any]:
    """
    Get credibility summary statistics across all reports.
    """
    avg_score = db.query(func.avg(ReportCredibility.score)).scalar() or 0.0
    max_score = db.query(func.max(ReportCredibility.score)).scalar() or 0
    min_score = db.query(func.min(ReportCredibility.score)).scalar() or 0

    # Level distribution counts
    levels = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW", "VERY_LOW"]
    distribution = {lvl: 0 for lvl in levels}
    
    counts = db.query(
        ReportCredibility.credibility_level,
        func.count(ReportCredibility.id)
    ).group_by(ReportCredibility.credibility_level).all()

    for lvl, count in counts:
        if lvl in distribution:
            distribution[lvl] = count

    return {
        "average_credibility": round(float(avg_score), 2),
        "highest_score": int(max_score),
        "lowest_score": int(min_score),
        "distribution_by_level": distribution,
    }
