import re

# Date formats patterns
# DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
DATE_DMY_PATTERN = re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2(20\d{2})\b')

# DD/MM/YY or DD-MM-YY
DATE_DMY_SHORT_PATTERN = re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2(\d{2})\b')

# MM/DD/YYYY or MM-DD-YYYY
DATE_MDY_PATTERN = re.compile(r'\b(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12][0-9]|3[01])\2(20\d{2})\b')

# MM/DD/YY or MM-DD-YY
DATE_MDY_SHORT_PATTERN = re.compile(r'\b(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12][0-9]|3[01])\2(\d{2})\b')

# YYYY/MM/DD or YYYY-MM-DD
DATE_YMD_PATTERN = re.compile(r'\b(20\d{2})([\/\-\.])(0?[1-9]|1[0-2])\2(0?[1-9]|[12][0-9]|3[01])\b')

# MM/YYYY or MM-YYYY
DATE_MY_PATTERN = re.compile(r'\b(0?[1-9]|1[0-2])(?:[\/\-\.])(20\d{2})\b')

# DD MMM YYYY or DD-MMM-YYYY (e.g. 12 May 2026, 12-Jan-2025)
DATE_TEXTUAL_DMY_PATTERN = re.compile(
    r'\b(0?[1-9]|[12][0-9]|3[01])[\s\-\.]?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*[\s\-\.]?(20\d{2})\b',
    re.IGNORECASE
)

# MMM YYYY (e.g. May 2026, Jan-2025)
DATE_TEXTUAL_MY_PATTERN = re.compile(
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*[\s\-\.]?(20\d{2})\b',
    re.IGNORECASE
)

# Field prefix patterns
MFG_PREFIX_PATTERN = re.compile(r'\b(?:mfg|mfd|mfg\.?date|packed|pkd|pkg)\b', re.IGNORECASE)
EXP_PREFIX_PATTERN = re.compile(r'\b(?:exp|expiry|exp\.?date|expiry\.?date|use\s*before|use\s*by|val)\b', re.IGNORECASE)
PKD_PREFIX_PATTERN = re.compile(r'\b(?:pkd|packed|packaging)\b', re.IGNORECASE)
BEST_BEFORE_PREFIX_PATTERN = re.compile(r'\b(?:best\s*before|bb|bby)\b', re.IGNORECASE)
BATCH_PREFIX_PATTERN = re.compile(r'\b(?:batch|b\.?no|lot|batch\s*no|b\s*no)\b', re.IGNORECASE)
LOT_PREFIX_PATTERN = re.compile(r'\b(?:lot|lot\s*no|l\.?no)\b', re.IGNORECASE)
MRP_PREFIX_PATTERN = re.compile(r'\b(?:mrp|price|rs\.?|maximum\s*retail\s*price)\b', re.IGNORECASE)

# Field inline extraction patterns
BATCH_PATTERN = re.compile(r'\b(?:batch|b\.?no|lot|b\s*no|batch\s*no)[:\- ]\s*([a-zA-Z0-9\-\/]+)', re.IGNORECASE)
LOT_PATTERN = re.compile(r'\b(?:lot|lot\s*no|l\.?no)[:\- ]\s*([a-zA-Z0-9\-\/]+)', re.IGNORECASE)
MRP_PATTERN = re.compile(r'\b(?:mrp|price|rs\.?)[:\- ]\s*(\d+(?:\.\d{2})?)', re.IGNORECASE)
WEIGHT_PATTERN = re.compile(r'\b(\d+(?:\.\d+)?\s*(?:g|kg|ml|l|oz|gm|gms|pcs|units))\b', re.IGNORECASE)
