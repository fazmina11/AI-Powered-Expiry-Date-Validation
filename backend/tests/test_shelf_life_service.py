"""
tests/test_shelf_life_service.py — Unit tests for the shelf-life decision engine.

All tests inject a fixed `today` date so results are deterministic
regardless of when the suite is run.

Covers every case from the Phase 1.4 spec:
  Case 1: 90 days remaining         → ACCEPTED
  Case 2: 45 days remaining         → PRIORITY_SALE
  Case 3: 10 days remaining         → REJECTED (below REJECT_DAYS=30)
  Case 4: already expired           → REJECTED
  Case 5: expiry before mfg date    → INVALID_DATE
  Case 6: expiry date missing       → MANUAL_REVIEW
"""

from datetime import date, timedelta

import pytest

from app.services.shelf_life_service import (
    evaluate_shelf_life,
    calculate_remaining_days,
    calculate_decision,   # backward-compat alias
)
from app.utils.constants import (
    ACCEPTED,
    INVALID_DATE,
    MANUAL_REVIEW,
    PRIORITY_SALE,
    REJECTED,
)

TODAY = date(2026, 6, 23)  # fixed reference date


# ── Helper ────────────────────────────────────────────────────

def test_calculate_remaining_days_future():
    future = TODAY + timedelta(days=90)
    assert calculate_remaining_days(future, TODAY) == 90


def test_calculate_remaining_days_past():
    past = TODAY - timedelta(days=5)
    assert calculate_remaining_days(past, TODAY) == -5


# ── Case 6: Missing expiry date → MANUAL_REVIEW ───────────────

def test_case6_missing_expiry_returns_manual_review():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 1, 1),
        expiry_date=None,
        today=TODAY,
    )
    assert result["status"] == MANUAL_REVIEW
    assert result["remaining_days"] is None
    assert "missing" in result["decision_reason"].lower()


def test_missing_both_dates_returns_manual_review():
    result = evaluate_shelf_life(None, None, today=TODAY)
    assert result["status"] == MANUAL_REVIEW


# ── Case 5: Expiry before manufacturing → INVALID_DATE ────────

def test_case5_expiry_before_mfg_returns_invalid_date():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 6, 1),
        expiry_date=date(2026, 5, 1),   # before mfg
        today=TODAY,
    )
    assert result["status"] == INVALID_DATE
    assert result["remaining_days"] is None
    assert "before" in result["decision_reason"].lower()


# ── Case 4: Already expired → REJECTED ────────────────────────

def test_case4_already_expired_returns_rejected():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 1, 1),
        expiry_date=TODAY - timedelta(days=1),
        today=TODAY,
    )
    assert result["status"] == REJECTED
    assert result["remaining_days"] < 0
    assert "expired" in result["decision_reason"].lower()


# ── Case 3: 10 days remaining → REJECTED ──────────────────────

def test_case3_10_days_remaining_returns_rejected():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 1, 1),
        expiry_date=TODAY + timedelta(days=10),
        today=TODAY,
    )
    assert result["status"] == REJECTED
    assert result["remaining_days"] == 10
    assert "minimum" in result["decision_reason"].lower()


# ── Case 2: 45 days remaining → PRIORITY_SALE ─────────────────

def test_case2_45_days_remaining_returns_priority_sale():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 1, 1),
        expiry_date=TODAY + timedelta(days=45),
        today=TODAY,
    )
    assert result["status"] == PRIORITY_SALE
    assert result["remaining_days"] == 45
    assert "prioritized" in result["decision_reason"].lower()


def test_boundary_exactly_at_reject_days_is_priority_sale():
    """remaining_days == REJECT_DAYS (30) → PRIORITY_SALE, not REJECTED."""
    result = evaluate_shelf_life(None, TODAY + timedelta(days=30), today=TODAY)
    assert result["status"] == PRIORITY_SALE


def test_boundary_exactly_at_warning_days_is_priority_sale():
    """remaining_days == WARNING_DAYS (60) → still PRIORITY_SALE."""
    result = evaluate_shelf_life(None, TODAY + timedelta(days=60), today=TODAY)
    assert result["status"] == PRIORITY_SALE


# ── Case 1: 90 days remaining → ACCEPTED ─────────────────────

def test_case1_90_days_remaining_returns_accepted():
    result = evaluate_shelf_life(
        manufacturing_date=date(2026, 1, 1),
        expiry_date=TODAY + timedelta(days=90),
        today=TODAY,
    )
    assert result["status"] == ACCEPTED
    assert result["remaining_days"] == 90
    assert "sufficient" in result["decision_reason"].lower()


def test_no_manufacturing_date_still_returns_accepted():
    result = evaluate_shelf_life(None, TODAY + timedelta(days=90), today=TODAY)
    assert result["status"] == ACCEPTED


# ── Return shape ──────────────────────────────────────────────

def test_result_always_has_all_keys():
    result = evaluate_shelf_life(None, TODAY + timedelta(days=90), today=TODAY)
    assert "status" in result
    assert "remaining_days" in result
    assert "decision_reason" in result


# ── Backward-compat alias ─────────────────────────────────────

def test_calculate_decision_alias_works():
    """calculate_decision must behave identically to evaluate_shelf_life."""
    r1 = evaluate_shelf_life(None, TODAY + timedelta(days=90), today=TODAY)
    r2 = calculate_decision(None, TODAY + timedelta(days=90), today=TODAY)
    assert r1 == r2
