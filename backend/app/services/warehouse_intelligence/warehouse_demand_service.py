"""
services/warehouse_intelligence/warehouse_demand_service.py — Service operations for Warehouse Demand Profiles.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.warehouse import WarehouseDemandProfile


def list_demand_profiles(
    db: Session,
    warehouse_id: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[WarehouseDemandProfile]:
    """Fetch demand profiles with optional warehouse and category filtering."""
    query = db.query(WarehouseDemandProfile)
    if warehouse_id:
        query = query.filter(WarehouseDemandProfile.warehouse_id == warehouse_id)
    if category:
        # Case-insensitive category comparison
        query = query.filter(WarehouseDemandProfile.product_category.ilike(category))
    return query.offset(skip).limit(limit).all()
