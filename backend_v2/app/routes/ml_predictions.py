from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.shelf_life_prediction_service import predict_pending_inventory_items

router = APIRouter()


@router.post("/process-pending")
def process_pending_ml_predictions(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    predictions = predict_pending_inventory_items(db, limit=limit)
    return {
        "success": True,
        "processed": len(predictions),
        "predictions": [
            {
                "id": str(prediction.id),
                "inventory_item_id": str(prediction.inventory_item_id),
                "decision": prediction.predicted_decision,
                "confidence": prediction.decision_confidence,
                "remaining_days": prediction.predicted_remaining_days,
            }
            for prediction in predictions
        ],
    }
