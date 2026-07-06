"""
services/warehouse_intelligence/transfer_cost_service.py — Service operations for Warehouse Transfer Cost Matrix.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.warehouse import WarehouseTransferMatrix


def list_transfer_matrix(
    db: Session,
    warehouse_id: Optional[str] = None,  # Match either source or destination
    source_warehouse_id: Optional[str] = None,
    destination_warehouse_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[WarehouseTransferMatrix]:
    """Fetch transfer cost matrix records with various optional filters."""
    query = db.query(WarehouseTransferMatrix)
    if source_warehouse_id:
        query = query.filter(WarehouseTransferMatrix.source_warehouse_id == source_warehouse_id)
    if destination_warehouse_id:
        query = query.filter(WarehouseTransferMatrix.destination_warehouse_id == destination_warehouse_id)
    if warehouse_id:
        # Match if it is either source or destination
        query = query.filter(
            (WarehouseTransferMatrix.source_warehouse_id == warehouse_id) |
            (WarehouseTransferMatrix.destination_warehouse_id == warehouse_id)
        )
    return query.offset(skip).limit(limit).all()
