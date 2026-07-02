"""
schemas/product.py — Compatibility shim.

The canonical schemas are in product_schema.py.
This file re-exports them so any existing import of
`app.schemas.product` continues to work without changes.
"""

from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse  # noqa: F401
