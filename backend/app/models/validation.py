"""
models/validation.py — Compatibility shim.

The canonical model file is validation_record.py.
This file re-exports ValidationRecord so existing imports continue to work
while the codebase migrates to the new filename convention.
"""

from app.models.validation_record import ValidationRecord  # noqa: F401
