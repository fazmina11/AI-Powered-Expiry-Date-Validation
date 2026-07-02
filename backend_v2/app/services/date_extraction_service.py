"""
services/date_extraction_service.py
Sprint 4 — Extract structured candidate fields from raw OCR text.

Fields extracted:
    candidate_mfg_date      Manufacturing / Packed date
    candidate_expiry_date   Expiry / Best Before date
    candidate_pkd_date      Packed-on date
    candidate_best_before   Best Before (when distinct from expiry)
    candidate_batch         Batch number string
    candidate_lot           Lot number string
    candidate_mrp           MRP value string

Supported date formats:
    DD/MM/YYYY   DD-MM-YYYY   DD.MM.YYYY
    YYYY-MM-DD   YYYY/MM/DD
    DD/MM/YY     DD-MM-YY     (2-digit year → 20YY)
    DD MMM YYYY  (textual)
    MMM YYYY     (textual, month-year only)

Scope:
    ✅  Pure text parsing — regex only
    ✅  Returns candidate strings (ISO dates where parseable)
    ❌  No database
    ❌  No FastAPI
    ❌  No ML inference
"""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from app.utils.regex_patterns import (
    # date patterns — all formats
    DATE_DMY_PATTERN,
    DATE_DMY_SHORT_PATTERN,
    DATE_MDY_PATTERN,
    DATE_MDY_SHORT_PATTERN,
    DATE_YMD_PATTERN,
    DATE_MY_PATTERN,
    DATE_TEXTUAL_DMY_PATTERN,
    DATE_TEXTUAL_MY_PATTERN,
    # field prefix patterns

    MFG_PREFIX_PATTERN,
    EXP_PREFIX_PATTERN,
    PKD_PREFIX_PATTERN,
    BEST_BEFORE_PREFIX_PATTERN,
    BATCH_PATTERN,
    LOT_PATTERN,
    MRP_PATTERN,
    WEIGHT_PATTERN,
)

# ── Month name → int ──────────────────────────────────────────────────────────
_MONTHS: dict[str, int] = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}

# Ordered list of (pattern, format_name) to try when scanning for dates
_DATE_SPECS = [
    (DATE_TEXTUAL_DMY_PATTERN, "textual_dmy"),  # 12 May 2026  — highest priority
    (DATE_DMY_PATTERN,         "dmy"),           # 12/05/2026
    (DATE_MDY_PATTERN,         "mdy"),           # 05/12/2026
    (DATE_YMD_PATTERN,         "ymd"),           # 2026-05-12
    (DATE_DMY_SHORT_PATTERN,   "dmy_short"),     # 12/05/26
    (DATE_MDY_SHORT_PATTERN,   "mdy_short"),     # 05/12/26
    (DATE_TEXTUAL_MY_PATTERN,  "textual_my"),    # May 2026
    (DATE_MY_PATTERN,          "my"),            # 05/2026
]



# ── Date parsing helpers ──────────────────────────────────────────────────────

def _to_date(day: Optional[str], month: str, year: str) -> Optional[date]:
    """Convert raw string groups → Python date. Returns None on any parse error."""
    try:
        y = int(year)
        if y < 100:                  # 2-digit year from DD/MM/YY
            y += 2000
        m = _MONTHS.get(month.lower(), None) or int(month)
        d = int(day) if day else 1   # default to 1st for month-only formats
        return date(y, m, d)
    except (ValueError, TypeError, AttributeError):
        return None


def _groups_to_date(groups: tuple, fmt: str) -> Optional[date]:
    """Unpack regex match groups by format name and delegate to _to_date."""
    if fmt == "dmy":
        # groups: (day, sep, month, year)
        d, _sep, m, y = groups
        return _to_date(d, m, y)
    if fmt == "mdy":
        # groups: (month, sep, day, year)
        m, _sep, d, y = groups
        return _to_date(d, m, y)
    if fmt == "dmy_short":
        # groups: (day, sep, month, year_2digit)
        d, _sep, m, y = groups
        return _to_date(d, m, y)
    if fmt == "mdy_short":
        # groups: (month, sep, day, year_2digit)
        m, _sep, d, y = groups
        return _to_date(d, m, y)
    if fmt == "ymd":
        # groups: (year, sep, month, day)
        y, _sep, m, d = groups
        return _to_date(d, m, y)
    if fmt == "textual_dmy":
        d, m, y = groups
        return _to_date(d, m, y)
    if fmt in ("my", "textual_my"):
        m, y = groups
        return _to_date(None, m, y)
    return None


def _lookback(text: str, pos: int, window: int = 35) -> str:
    """Return the slice of text immediately before `pos`."""
    return text[max(0, pos - window): pos]


# ── Core extraction ───────────────────────────────────────────────────────────

from dateutil.relativedelta import relativedelta

# Regex to match relative shelf-life durations (e.g. "best before 90 days")
RELATIVE_SHELF_LIFE_PATTERNS = [
    re.compile(r'\bbest\s+before\s+(\d+)\s*(days|months|years|day|month|year)?(?:\s+from\s+(?:mfg|mfd|manuf|packing|pack))?', re.IGNORECASE),
    re.compile(r'\buse\s+within\s+(\d+)\s*(days|months|years|day|month|year)?\b', re.IGNORECASE),
    re.compile(r'\bshelf\s*life\s*[:\-]?\s*(\d+)\s*(days|months|years|day|month|year)?\b', re.IGNORECASE),
    re.compile(r'\b(\d+)\s*(days|months|years|day|month|year)\s*from\s*(?:mfg|mfd|manuf|packing|pack|pkd)', re.IGNORECASE),
]

def extract_relative_shelf_life(text: str) -> tuple[int, str] | None:
    """
    Search text for relative shelf-life expressions.
    Returns (quantity, unit) or None.
    Example: 'best before 6 months' -> (6, 'months')
    """
    for pattern in RELATIVE_SHELF_LIFE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                qty = int(match.group(1))
                unit = match.group(2) if len(match.groups()) > 1 and match.group(2) else "days"
                return qty, unit.lower()
            except (ValueError, TypeError):
                continue
    return None


class ExtractionResult:
    """Holds all candidate fields found in a single OCR text."""

    __slots__ = (
        "candidate_product_name",
        "candidate_mfg_date",
        "candidate_expiry_date",
        "candidate_pkd_date",
        "candidate_best_before",
        "candidate_batch",
        "candidate_lot",
        "candidate_mrp",
        "candidate_weight",
        "all_dates_found",
        "candidate_shelf_life_qty",
        "candidate_shelf_life_unit",
        "exp_computed",
    )

    def __init__(self) -> None:
        self.candidate_product_name: Optional[str] = None
        self.candidate_mfg_date:    Optional[str] = None
        self.candidate_expiry_date: Optional[str] = None
        self.candidate_pkd_date:    Optional[str] = None
        self.candidate_best_before: Optional[str] = None
        self.candidate_batch:       Optional[str] = None
        self.candidate_lot:         Optional[str] = None
        self.candidate_mrp:         Optional[str] = None
        self.candidate_weight:      Optional[str] = None
        self.all_dates_found:       list[str]     = []
        self.candidate_shelf_life_qty: Optional[int] = None
        self.candidate_shelf_life_unit: Optional[str] = None
        self.exp_computed:          bool          = False

    def to_dict(self) -> dict:
        return {
            "candidate_product_name": self.candidate_product_name,
            "candidate_mfg_date":    self.candidate_mfg_date,
            "candidate_expiry_date": self.candidate_expiry_date,
            "candidate_pkd_date":    self.candidate_pkd_date,
            "candidate_best_before": self.candidate_best_before,
            "candidate_batch":       self.candidate_batch,
            "candidate_lot":         self.candidate_lot,
            "candidate_mrp":         self.candidate_mrp,
            "candidate_weight":      self.candidate_weight,
            "all_dates_found":       self.all_dates_found,
            "candidate_shelf_life_qty": self.candidate_shelf_life_qty,
            "candidate_shelf_life_unit": self.candidate_shelf_life_unit,
            "exp_computed":          self.exp_computed,
        }


# Digit confusion mapping for OCR errors in dates
DATE_CANDIDATE = re.compile(r'\b[A-Za-z0-9]{1,4}[/\-.][A-Za-z0-9]{1,4}[/\-.][A-Za-z0-9]{2,4}\b')
DIGIT_CONFUSION = {'O': '0', 'I': '1', 'L': '1', 'S': '5', 'B': '8', 'Z': '2'}

def clean_date_candidate(candidate: str) -> str:
    """Replace confused alphabetical characters with numeric digits in date candidates."""
    return ''.join(DIGIT_CONFUSION.get(ch, ch) for ch in candidate.upper())


def clean_date_substrings(text: str) -> str:
    """Find date-like patterns in text and apply clean_date_candidate to them."""
    def replace_match(m):
        return clean_date_candidate(m.group(0))
    return DATE_CANDIDATE.sub(replace_match, text)


def extract_fields(raw_text: str) -> ExtractionResult:
    """
    Scan OCR raw_text and extract all candidate label fields.

    Args:
        raw_text: Plain-text string returned by paddle_ocr_service.extract_text().

    Returns:
        ExtractionResult with populated candidate fields.
        Fields are ISO-format date strings ("YYYY-MM-DD") or plain strings.
    """
    result = ExtractionResult()
    if not raw_text or not raw_text.strip():
        return result

    # ── Pass 0: Clean up date-like substrings of digit confusion (e.g. 09/O6/26 -> 09/06/26)
    raw_text = clean_date_substrings(raw_text)

    # ── Pass 1: collect every date with its position and context label ────────
    # List of (date_obj, start_pos, matched_text)
    dated: list[tuple[date, int, str]] = []

    for pattern, fmt in _DATE_SPECS:
        for m in pattern.finditer(raw_text):
            d = _groups_to_date(m.groups(), fmt)
            if d:
                # Avoid duplicate positions from overlapping patterns
                if not any(abs(m.start() - pos) < 3 for _, pos, _ in dated):
                    dated.append((d, m.start(), m.group()))

    # Sort by position in text (top-of-label → bottom)
    dated.sort(key=lambda t: t[1])
    result.all_dates_found = [d.isoformat() for d, _, _ in dated]

    # ── Pass 2: classify each date by surrounding context ────────────────────
    for d, pos, matched in dated:
        lookback = _lookback(raw_text, pos)
        lookahead = raw_text[pos: pos + len(matched) + 40]  # small lookahead too

        context = lookback + " " + lookahead

        is_mfg  = bool(MFG_PREFIX_PATTERN.search(context))
        is_exp  = bool(EXP_PREFIX_PATTERN.search(context))
        is_pkd  = bool(PKD_PREFIX_PATTERN.search(context))
        is_bb   = bool(BEST_BEFORE_PREFIX_PATTERN.search(context))

        iso = d.isoformat()

        if is_pkd and not result.candidate_pkd_date:
            result.candidate_pkd_date = iso
        elif is_bb and not result.candidate_best_before:
            result.candidate_best_before = iso
            # Also fill expiry if empty — best_before IS the expiry
            if not result.candidate_expiry_date:
                result.candidate_expiry_date = iso
        elif is_mfg and not result.candidate_mfg_date:
            result.candidate_mfg_date = iso
        elif is_exp and not result.candidate_expiry_date:
            result.candidate_expiry_date = iso

    # ── Pass 3: chronological heuristic fallback ──────────────────────────────
    # If we have ≥2 unclassified dates, assume earlier = MFG, later = EXP
    if dated and (not result.candidate_mfg_date or not result.candidate_expiry_date):
        unclassified = [
            d for d, _, _ in dated
            if d.isoformat() not in (
                result.candidate_mfg_date,
                result.candidate_expiry_date,
                result.candidate_pkd_date,
                result.candidate_best_before,
            )
        ]
        if len(unclassified) >= 2:
            unclassified.sort()
            if not result.candidate_mfg_date:
                result.candidate_mfg_date = unclassified[0].isoformat()
            if not result.candidate_expiry_date:
                result.candidate_expiry_date = unclassified[-1].isoformat()
        elif len(unclassified) == 1:
            # Single unclassified date — assign to whichever slot is empty
            if not result.candidate_expiry_date:
                result.candidate_expiry_date = unclassified[0].isoformat()
            elif not result.candidate_mfg_date:
                result.candidate_mfg_date = unclassified[0].isoformat()

    # ── Pass 3.5: Relative shelf-life calculations ────────────────────────────
    shelf_life = extract_relative_shelf_life(raw_text)
    if shelf_life:
        qty, unit = shelf_life
        result.candidate_shelf_life_qty = qty
        result.candidate_shelf_life_unit = unit
        # If we have MFG date, we can calculate expiry date!
        if result.candidate_mfg_date and not result.candidate_expiry_date:
            try:
                from datetime import datetime
                import logging
                logger = logging.getLogger(__name__)

                mfg_dt = datetime.strptime(result.candidate_mfg_date, "%Y-%m-%d").date()
                if "month" in unit:
                    exp_dt = mfg_dt + relativedelta(months=qty)
                elif "year" in unit:
                    exp_dt = mfg_dt + relativedelta(years=qty)
                else:
                    exp_dt = mfg_dt + relativedelta(days=qty)
                result.candidate_expiry_date = exp_dt.isoformat()
                result.exp_computed = True
                logger.info("[Extraction] Computed expiry date %s from mfg %s using relative rule (%d %s)",
                            result.candidate_expiry_date, result.candidate_mfg_date, qty, unit)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("[Extraction] Relative calculation failed: %s", e)

    # ── Pass 4: non-date fields ───────────────────────────────────────────────
    batch_m = BATCH_PATTERN.search(raw_text)
    if batch_m:
        result.candidate_batch = batch_m.group(1).strip().upper()

    lot_m = LOT_PATTERN.search(raw_text)
    if lot_m:
        result.candidate_lot = lot_m.group(1).strip().upper()

    mrp_m = MRP_PATTERN.search(raw_text)
    if mrp_m:
        result.candidate_mrp = mrp_m.group(1).strip()

    weight_m = WEIGHT_PATTERN.search(raw_text)
    if weight_m:
        result.candidate_weight = (weight_m.group(1) or weight_m.group(2)).strip()

    # ── Pass 5: Product Name Heuristic ────────────────────────────────────────
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines[:3]:
        # Skip lines that look like standard fields
        if any(p.search(line) for p in (MFG_PREFIX_PATTERN, EXP_PREFIX_PATTERN, PKD_PREFIX_PATTERN, BATCH_PATTERN, MRP_PATTERN, WEIGHT_PATTERN)):
            continue
        # Check if mostly text
        if re.match(r"^[A-Za-z0-9\s\.\,\'\&\-]+$", line) and len(line) > 2:
            result.candidate_product_name = line
            break

    return result


# ══════════════════════════════════════════════════════════════════
#  Compatibility shim — Member 2's ocr_routes.py imports this name.
#  DO NOT REMOVE.
# ══════════════════════════════════════════════════════════════════

def extract_dates_from_text(raw_text: str) -> dict:
    """
    Shim wrapper: returns the simple dict format expected by
    Member 2's /ocr/extract-dates endpoint.
    """
    result = extract_fields(raw_text)
    return {
        "mfg_date":    result.candidate_mfg_date,
        "expiry_date": result.candidate_expiry_date,
    }
