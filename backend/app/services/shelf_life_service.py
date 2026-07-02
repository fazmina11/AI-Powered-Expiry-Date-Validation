"""
services/shelf_life_service.py — Shelf-life decision engine.

Pure business logic — no I/O, no database access.
Injectable `today` parameter makes every decision deterministically testable.

Decision priority order (evaluated top to bottom):
  1. Missing expiry date           → MANUAL_REVIEW
  2. Expiry before manufacturing   → INVALID_DATE
  3. Already expired               → REJECTED
  4. remaining_days < REJECT_DAYS  → REJECTED
  5. remaining_days <= WARNING_DAYS → PRIORITY_SALE
  6. remaining_days > WARNING_DAYS  → ACCEPTED
"""

from datetime import date
from typing import Optional, TypedDict

from app.config import settings
from app.utils.constants import (
    ACCEPTED,
    INVALID_DATE,
    MANUAL_REVIEW,
    PRIORITY_SALE,
    REJECTED,
)


class ShelfLifeResult(TypedDict):
    status: str
    remaining_days: Optional[int]
    decision_reason: str


# ── Helper ────────────────────────────────────────────────────

def calculate_remaining_days(expiry_date: date, today: Optional[date] = None) -> int:
    """Return the number of days between today and expiry_date (can be negative)."""
    if today is None:
        today = date.today()
    return (expiry_date - today).days


# ── Main entry point ──────────────────────────────────────────

def evaluate_shelf_life(
    manufacturing_date: Optional[date],
    expiry_date: Optional[date],
    today: Optional[date] = None,
) -> ShelfLifeResult:
    """
    Evaluate the shelf-life status of a product batch.

    Args:
        manufacturing_date: Date the product was manufactured (optional).
        expiry_date:        Best-before / expiry date (optional).
        today:              Reference date for calculations. Defaults to date.today().
                            Inject a fixed date in tests for deterministic results.

    Returns:
        ShelfLifeResult with keys: status, remaining_days, decision_reason.
    """
    if today is None:
        today = date.today()

    # ── Rule 1: Missing expiry date ───────────────────────────
    if expiry_date is None:
        return ShelfLifeResult(
            status=MANUAL_REVIEW,
            remaining_days=None,
            decision_reason="Expiry date is missing. Manual review required.",
        )

    # ── Rule 2: Expiry before manufacturing ───────────────────
    if manufacturing_date is not None and expiry_date < manufacturing_date:
        return ShelfLifeResult(
            status=INVALID_DATE,
            remaining_days=None,
            decision_reason="Expiry date cannot be before manufacturing date.",
        )

    remaining_days = calculate_remaining_days(expiry_date, today)

    # ── Rule 3: Already expired ───────────────────────────────
    if expiry_date < today:
        return ShelfLifeResult(
            status=REJECTED,
            remaining_days=remaining_days,
            decision_reason="Product is already expired.",
        )

    # ── Rule 4: Below reject threshold ───────────────────────
    if remaining_days < settings.REJECT_DAYS:
        return ShelfLifeResult(
            status=REJECTED,
            remaining_days=remaining_days,
            decision_reason="Product has less than minimum required shelf life.",
        )

    # ── Rule 5: Nearing expiry ────────────────────────────────
    if remaining_days <= settings.WARNING_DAYS:
        return ShelfLifeResult(
            status=PRIORITY_SALE,
            remaining_days=remaining_days,
            decision_reason="Product has limited shelf life and should be prioritized for sale.",
        )

    # ── Rule 6: Acceptable shelf life ────────────────────────
    return ShelfLifeResult(
        status=ACCEPTED,
        remaining_days=remaining_days,
        decision_reason="Product has sufficient shelf life.",
    )


# ── Backward-compatible alias ─────────────────────────────────
# Existing code that calls calculate_decision() continues to work.
calculate_decision = evaluate_shelf_life
