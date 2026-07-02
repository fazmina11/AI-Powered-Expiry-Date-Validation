"""
schemas/inventory.py — Compatibility shim.

Canonical schemas are in inventory_schema.py.
Re-exports everything so existing imports continue to work.
"""

from app.schemas.inventory_schema import (  # noqa: F401
    InventoryIntakeRequest,
    InventoryResponse,
    InventoryListResponse,
)
