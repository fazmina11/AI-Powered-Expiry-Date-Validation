"""
services/warehouse_intelligence/warehouse_config_service.py — Service operations for Warehouse Configurations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.warehouse import WarehouseConfiguration


def get_configuration(db: Session, warehouse_id: str) -> Optional[WarehouseConfiguration]:
    """Fetch configuration for a specific warehouse ID."""
    return db.query(WarehouseConfiguration).filter(
        WarehouseConfiguration.warehouse_id == warehouse_id
    ).first()


def list_configurations(
    db: Session,
    warehouse_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[WarehouseConfiguration]:
    """Fetch configurations with optional warehouse filtering."""
    query = db.query(WarehouseConfiguration)
    if warehouse_id:
        query = query.filter(WarehouseConfiguration.warehouse_id == warehouse_id)
    return query.offset(skip).limit(limit).all()
