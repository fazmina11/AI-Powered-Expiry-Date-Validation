"""
services/gs1_barcode_service.py
Sprint 5 — GS1 DataMatrix (2D square barcode) direct parser using zxing-cpp.
Reuses the stable zxing-cpp library to decode 2D DataMatrix barcodes,
avoiding Windows ctypes DLL dependency load errors completely.
"""

from __future__ import annotations

import re
import logging
from datetime import datetime
import zxingcpp

logger = logging.getLogger(__name__)

# GS1 Application Identifiers relevant to this system
AI_GTIN = '01'
AI_BATCH = '10'
AI_MFG_DATE = '11'
AI_EXP_DATE = '17'

# GS1 AIs are either fixed-length or variable-length (terminated by FNC1, ASCII 0x1D)
FIXED_LENGTH_AIS = {
    '01': 14,  # GTIN
    '11': 6,   # MFG date YYMMDD
    '17': 6,   # EXP date YYMMDD
}
GS1_SEPARATOR = '\x1d'  # FNC1 group separator for variable-length fields like batch (10)


def detect_and_decode_datamatrix(image_bgr) -> str | None:
    """
    Attempts to find and decode a GS1 DataMatrix (square 2D barcode) in the image.
    Uses zxing-cpp for stable Windows execution.
    """
    try:
        barcodes = zxingcpp.read_barcodes(image_bgr)
        for bc in barcodes:
            # We target DATA_MATRIX format specifically
            if bc.format.name in ("DATA_MATRIX", "DATAMATRIX"):
                return bc.text
        # Fallback: if format is not explicitly named DATA_MATRIX but starts with GS1 format
        for bc in barcodes:
            if bc.text and bc.text.startswith("(01)"):
                return bc.text
    except Exception as exc:
        logger.error("[GS1Service] Datamatrix decoding failed: %s", exc, exc_info=True)
    return None


def parse_gs1_string(raw: str) -> dict:
    """
    Parses a raw GS1 element string into a dict of AI -> value.
    Handles both fixed-length AIs (01, 11, 17) and variable-length AIs (10, terminated
    by FNC1 separator or end of string).
    """
    parsed = {}
    i = 0
    # Clean brackets if zxing returned formatted string like (01)08901058850817(17)260630(10)LOT
    if raw.startswith("("):
        # Match all (AI)value pairs
        pattern = re.findall(r'\((\d{2,4})\)([^(]+)', raw)
        for ai, val in pattern:
            parsed[ai] = val.strip()
        return parsed

    while i < len(raw):
        ai = raw[i:i+2]
        i += 2

        if ai in FIXED_LENGTH_AIS:
            length = FIXED_LENGTH_AIS[ai]
            value = raw[i:i+length]
            i += length
        else:
            # Variable length — read until separator or end of string
            sep_index = raw.find(GS1_SEPARATOR, i)
            if sep_index == -1:
                value = raw[i:]
                i = len(raw)
            else:
                value = raw[i:sep_index]
                i = sep_index + 1

        parsed[ai] = value

    return parsed


def gs1_date_to_iso(yy_mm_dd: str) -> str | None:
    """
    Converts GS1 date format YYMMDD to DD/MM/YYYY.
    GS1 rule: YY 00-50 => 2000-2050, YY 51-99 => 1951-1999.
    """
    if not yy_mm_dd or len(yy_mm_dd) != 6 or not yy_mm_dd.isdigit():
        return None

    try:
        yy, mm, dd = int(yy_mm_dd[0:2]), int(yy_mm_dd[2:4]), int(yy_mm_dd[4:6])
        year = 2000 + yy if yy <= 50 else 1900 + yy

        if dd == 0:
            dd = 1  # treat as first of month

        return datetime(year, mm, dd).strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return None


def extract_dates_from_datamatrix(image_bgr) -> dict:
    """
    Main entry point. Returns:
    {
        'found': bool,
        'gtin': str or None,
        'mfg': 'DD/MM/YYYY' or None,
        'exp': 'DD/MM/YYYY' or None,
        'batch': str or None,
    }
    """
    raw = detect_and_decode_datamatrix(image_bgr)
    if not raw:
        return {'found': False, 'gtin': None, 'mfg': None, 'exp': None, 'batch': None}

    fields = parse_gs1_string(raw)

    return {
        'found': True,
        'gtin': fields.get(AI_GTIN),
        'mfg': gs1_date_to_iso(fields.get(AI_MFG_DATE)),
        'exp': gs1_date_to_iso(fields.get(AI_EXP_DATE)),
        'batch': fields.get(AI_BATCH),
    }
