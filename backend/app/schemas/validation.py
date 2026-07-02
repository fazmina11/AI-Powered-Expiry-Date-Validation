"""
schemas/validation.py — Compatibility shim.

Canonical schemas are in validation_schema.py.
Re-exports everything so existing imports continue to work.
ValidationManualCreate is kept as an alias for ValidationCreate.
"""

from app.schemas.validation_schema import (  # noqa: F401
    ValidationCreate,
    ValidationResponse,
)

# Backward-compat alias used by existing route and tests
ValidationManualCreate = ValidationCreate
