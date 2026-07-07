import re

# ── Date format patterns ───────────────────────────────────────────────────────
#
# NOTE: Short-date patterns do NOT use \b at the start because OCR output
# often embeds dates mid-token (e.g. "MFD12/05/26") with no whitespace boundary.
# The (?<!\d) negative lookbehind prevents matching inside a longer number.

# DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY  (4-digit year)
DATE_DMY_PATTERN = re.compile(
    r'(?<!\d)(0?[1-9]|[12][0-9]|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2(20\d{2})(?!\d)'
)

# DD/MM/YY or DD-MM-YY  (2-digit year)
DATE_DMY_SHORT_PATTERN = re.compile(
    r'(?<!\d)(0?[1-9]|[12][0-9]|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2(\d{2})(?!\d)'
)

# MM/DD/YYYY or MM-DD-YYYY  (4-digit year)
DATE_MDY_PATTERN = re.compile(
    r'(?<!\d)(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12][0-9]|3[01])\2(20\d{2})(?!\d)'
)

# MM/DD/YY or MM-DD-YY  (2-digit year)
DATE_MDY_SHORT_PATTERN = re.compile(
    r'(?<!\d)(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12][0-9]|3[01])\2(\d{2})(?!\d)'
)

# YYYY/MM/DD or YYYY-MM-DD
DATE_YMD_PATTERN = re.compile(
    r'\b(20\d{2})([\/\-\.])(0?[1-9]|1[0-2])\2(0?[1-9]|[12][0-9]|3[01])\b'
)

# MM/YYYY or MM-YYYY  (month-year only)
DATE_MY_PATTERN = re.compile(r'(?<!\d)(0?[1-9]|1[0-2])(?:[\/\-\.])(20\d{2})(?!\d)')

# DD MMM YYYY or DD-MMM-YYYY  (e.g. 12 May 2026, 12-Jan-2025)
DATE_TEXTUAL_DMY_PATTERN = re.compile(
    r'\b(0?[1-9]|[12][0-9]|3[01])[\s\-\.]?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*[\s\-\.]?(20\d{2})\b',
    re.IGNORECASE
)

# MMM YYYY  (e.g. May 2026, Jan-2025)
DATE_TEXTUAL_MY_PATTERN = re.compile(
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*[\s\-\.]?(20\d{2})\b',
    re.IGNORECASE
)

# ── Field prefix patterns ─────────────────────────────────────────────────────
#
# Indian product labels use many abbreviations — all common variants are included.

MFG_PREFIX_PATTERN = re.compile(
    r'\b(?:mfg|mfd|mfg\.?\s*date|mfd\.?\s*date|manufactured|manuf|'
    r'packed\s*on|pkd|pkg|p\.?k\.?d|m\.?f\.?d|m\.?f\.?g|'
    r'date\s*of\s*mfg|date\s*of\s*manufacture|dom|d\.?o\.?m)\b',
    re.IGNORECASE
)

EXP_PREFIX_PATTERN = re.compile(
    r'\b(?:exp|expiry|exp\.?\s*date|expiry\.?\s*date|expires|'
    r'use\s*before|use\s*by|u\.?b|best\s*before\s*end|bbe|'
    r'use\s*&\s*sell\s*by|sell\s*by|best\s*if\s*used\s*by|'
    r'val(?:idity)?|bb|bby|b\.?b\.?e|b\.?b|'
    r'date\s*of\s*exp(?:iry)?|doe|d\.?o\.?e|'
    r'good\s*(?:thru|through|till|until))\b',
    re.IGNORECASE
)

PKD_PREFIX_PATTERN = re.compile(
    r'\b(?:pkd|packed|packaging|pack(?:ed)?\s*on|p\.?k\.?d)\b',
    re.IGNORECASE
)

BEST_BEFORE_PREFIX_PATTERN = re.compile(
    r'\b(?:best\s*before|bb|bby|b\.?b|best\s*by)\b',
    re.IGNORECASE
)

BATCH_PREFIX_PATTERN = re.compile(
    r'\b(?:batch|b\.?no|lot|batch\s*no|b\s*no)\b',
    re.IGNORECASE
)

LOT_PREFIX_PATTERN = re.compile(
    r'\b(?:lot|lot\s*no|l\.?no)\b',
    re.IGNORECASE
)

MRP_PREFIX_PATTERN = re.compile(
    r'\b(?:mrp|price|rs\.?|maximum\s*retail\s*price)\b',
    re.IGNORECASE
)

# ── Field inline extraction patterns ─────────────────────────────────────────

BATCH_PATTERN = re.compile(
    r'\b(?:batch|b\.?no|lot|b\s*no|batch\s*no)[:\-\s]\s*([a-zA-Z0-9\-\/]+)',
    re.IGNORECASE
)

LOT_PATTERN = re.compile(
    r'\b(?:lot|lot\s*no|l\.?no)[:\-\s]\s*([a-zA-Z0-9\-\/]+)',
    re.IGNORECASE
)

MRP_PATTERN = re.compile(
    r'\b(?:mrp|price|rs\.?)[:\-\s]\s*(\d+(?:\.\d{2})?)',
    re.IGNORECASE
)

WEIGHT_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?\s*(?:g|kg|ml|l|oz|gm|gms|pcs|units))\b',
    re.IGNORECASE
)
