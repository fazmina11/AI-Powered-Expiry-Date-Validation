from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.ml_prediction import MLPrediction


MODEL_NAME = "local-shelf-life-rules"
MODEL_VERSION = "1.0.0"
PRIORITY_SALE_DAYS = 30


def _days_remaining(expiry_date: Optional[date], today: Optional[date] = None) -> Optional[int]:
    if not expiry_date:
        return None
    today = today or date.today()
    return (expiry_date - today).days


def _confidence(item: InventoryItem, remaining_days: Optional[int]) -> float:
    score = 0.55
    if item.expiry_date:
        score += 0.25
    if item.manufacturing_date:
        score += 0.10
    if item.batch_number:
        score += 0.05
    if remaining_days is not None:
        score += 0.05
    if item.manufacturing_date and item.expiry_date and item.manufacturing_date > item.expiry_date:
        score = min(score, 0.45)
    return round(min(score, 0.98), 4)


def predict_inventory_item(
    db: Session,
    item: InventoryItem,
    *,
    today: Optional[date] = None,
) -> MLPrediction:
    remaining_days = _days_remaining(item.expiry_date, today)
    confidence = _confidence(item, remaining_days)

    if item.manufacturing_date and item.expiry_date and item.manufacturing_date > item.expiry_date:
        decision = "REQUIRES_REVIEW"
        reason = "Manufacturing date is after expiry date."
    elif remaining_days is None:
        decision = "REQUIRES_REVIEW"
        reason = "Expiry date is missing."
    elif remaining_days < 0:
        decision = "REJECTED"
        reason = "Product is already expired."
    elif remaining_days <= PRIORITY_SALE_DAYS:
        decision = "PRIORITY_SALE"
        reason = "Product is nearing expiry; prioritize immediate sale."
    else:
        decision = "ACCEPTED"
        reason = "Product has sufficient shelf life remaining."

    # Placeholder for a future temperature-aware model. Keeping both fields
    # populated makes frontend/database behavior consistent today.
    adjusted_remaining = float(remaining_days) if remaining_days is not None else None
    arrhenius_remaining = adjusted_remaining

    prediction = MLPrediction(
        inventory_item_id=item.id,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        predicted_mfg_date=item.manufacturing_date,
        predicted_expiry_date=item.expiry_date,
        predicted_remaining_days=remaining_days,
        predicted_decision=decision,
        decision_confidence=confidence,
        decision_reason=reason,
        raw_prediction_payload=json.dumps(
            {
                "remaining_days": remaining_days,
                "adjusted_remaining": adjusted_remaining,
                "arrhenius_remaining": arrhenius_remaining,
                "decision": decision,
                "confidence": confidence,
                "reason": reason,
            }
        ),
        prediction_status="completed",
        predicted_at=datetime.now(timezone.utc),
    )
    db.add(prediction)

    item.ml_status = "COMPLETED"
    item.ml_decision = decision
    item.ml_confidence = confidence
    item.adjusted_remaining = adjusted_remaining
    item.arrhenius_remaining = arrhenius_remaining
    item.ml_processed_at = datetime.now(timezone.utc)
    item.pipeline_status = "ML_COMPLETED"
    item.status_reason = reason

    return prediction


def predict_pending_inventory_items(db: Session, limit: int = 100) -> list[MLPrediction]:
    items = (
        db.query(InventoryItem)
        .filter((InventoryItem.ml_status.is_(None)) | (InventoryItem.ml_status != "COMPLETED"))
        .order_by(InventoryItem.created_at.asc())
        .limit(limit)
        .all()
    )

    predictions: list[MLPrediction] = []
    for item in items:
        predictions.append(predict_inventory_item(db, item))

    db.commit()
    return predictions
