"""
services/warehouse_intelligence/supplier_return_service.py — Service operations for Supplier Return Policies.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.warehouse import SupplierReturnPolicy


def get_supplier_policy(db: Session, supplier_id: str) -> Optional[SupplierReturnPolicy]:
    """Fetch return policy for a specific supplier ID."""
    return db.query(SupplierReturnPolicy).filter(
        SupplierReturnPolicy.supplier_id == supplier_id
    ).first()


def list_supplier_policies(
    db: Session,
    supplier_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[SupplierReturnPolicy]:
    """Fetch supplier return policies with optional supplier filtering."""
    query = db.query(SupplierReturnPolicy)
    if supplier_id:
        # Support partial/exact matching
        query = query.filter(SupplierReturnPolicy.supplier_id.ilike(f"%{supplier_id}%"))
    return query.offset(skip).limit(limit).all()
