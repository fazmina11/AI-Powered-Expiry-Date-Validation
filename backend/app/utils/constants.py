"""
utils/constants.py — Single source of truth for all status string literals.

Import these everywhere instead of bare strings to prevent typos
and make refactoring safe.
"""

# ── Inventory / shelf-life decision statuses ──────────────────
PENDING       = "PENDING"        # Default: not yet evaluated
ACCEPTED      = "ACCEPTED"       # Sufficient shelf life
PRIORITY_SALE = "PRIORITY_SALE"  # Nearing expiry — sell first
REJECTED      = "REJECTED"       # Expired or below minimum threshold
MANUAL_REVIEW = "MANUAL_REVIEW"  # Missing data — human review needed
INVALID_DATE  = "INVALID_DATE"   # Data integrity error (expiry < mfg)

DECISION_STATUSES = {PENDING, ACCEPTED, PRIORITY_SALE, REJECTED, MANUAL_REVIEW, INVALID_DATE}

# ── Validation record statuses ────────────────────────────────
VALID          = "VALID"          # confidence_score >= 0.80
LOW_CONFIDENCE = "LOW_CONFIDENCE" # confidence_score < 0.80
# MANUAL_REVIEW is shared with inventory statuses (already defined above)

VALIDATION_STATUSES = {VALID, LOW_CONFIDENCE, MANUAL_REVIEW}
