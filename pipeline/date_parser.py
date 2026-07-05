import re
from datetime import datetime


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

EXP_KEYWORDS = ("exp", "expiry", "expires", "use by", "best before", "bb", "bbd")
MFG_KEYWORDS = ("mfg", "mfd", "manufactured", "manufacturing", "pkd", "packed", "pkg")

DATE_CANDIDATE = re.compile(r"\b[A-Za-z0-9]{1,4}[/\-.][A-Za-z0-9]{1,4}(?:[/\-.][A-Za-z0-9]{2,4})?\b")
DIGIT_CONFUSION = {
    "O": "0",
    "Q": "0",
    "D": "0",
    "T": "1",
    "I": "1",
    "L": "1",
    "S": "5",
    "B": "8",
    "Z": "2",
    "G": "6",
}

DATE_PATTERNS = [
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])([/\-.])(0?[1-9]|1[0-2])\2((?:19|20)\d{2})\b"), "dmy"),
    (re.compile(r"\b((?:19|20)\d{2})([/\-.])(0?[1-9]|1[0-2])\2(0?[1-9]|[12]\d|3[01])\b"), "ymd"),
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])([/\-.])(0?[1-9]|1[0-2])\2(\d{2})\b"), "dmy_short"),
    (re.compile(r"\b(0?[1-9]|1[0-2])([/\-.])((?:19|20)\d{2})\b"), "my"),
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])\s+([A-Za-z]{3,9})\s+((?:19|20)\d{2})\b", re.IGNORECASE), "text_dmy"),
    (re.compile(r"\b([A-Za-z]{3,9})\s+(0?[1-9]|[12]\d|3[01]),?\s+((?:19|20)\d{2})\b", re.IGNORECASE), "text_mdy"),
    (re.compile(r"\b([A-Za-z]{3,9})\s+((?:19|20)\d{2})\b", re.IGNORECASE), "text_my"),
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])\s+([A-Za-z]{3,9})(?:\s+[A-Za-z:]{2,12}){1,4}\s+((?:19|20)\d{2}|20\d)\b", re.IGNORECASE), "text_dmy_noisy"),
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])([/\-.])(0?[1-9]|1[0-2])\2?\b"), "dm_missing_year"),
    (re.compile(r"\b(0?[1-9]|[12]\d|3[01])\s+([A-Za-z]{3,9})\b", re.IGNORECASE), "text_dm_missing_year"),
]


def _normalize_ocr_date_noise(text):
    def replace_candidate(match):
        return "".join(DIGIT_CONFUSION.get(ch, ch) for ch in match.group(0).upper())

    normalized = DATE_CANDIDATE.sub(replace_candidate, text)
    normalized = re.sub(r"\s+([/\-.])", r"\1", normalized)
    normalized = re.sub(r"([/\-.])\s+", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _two_digit_year(year):
    value = int(year)
    return 2000 + value if value < 50 else 1900 + value


def _build_date(day, month, year):
    try:
        month_value = MONTHS.get(str(month).lower(), None) or int(month)
        year_int = int(year)
        if 100 <= year_int < 1000 and str(year_int).startswith("20"):
            year_int = datetime.now().year
        year_value = _two_digit_year(year) if year_int < 100 else year_int
        return datetime(year_value, month_value, int(day))
    except (TypeError, ValueError):
        return None


def _parse_match(match, fmt):
    groups = match.groups()
    if fmt == "dmy":
        day, _sep, month, year = groups
        return _build_date(day, month, year)
    if fmt == "ymd":
        year, _sep, month, day = groups
        return _build_date(day, month, year)
    if fmt == "dmy_short":
        day, _sep, month, year = groups
        return _build_date(day, month, year)
    if fmt == "my":
        month, _sep, year = groups
        return _build_date(1, month, year)
    if fmt in ("text_dmy", "text_dmy_noisy"):
        day, month, year = groups
        return _build_date(day, month, year)
    if fmt == "text_mdy":
        month, day, year = groups
        return _build_date(day, month, year)
    if fmt == "text_my":
        month, year = groups
        return _build_date(1, month, year)
    if fmt == "dm_missing_year":
        day, _sep, month = groups
        return _build_date(day, month, datetime.now().year)
    if fmt == "text_dm_missing_year":
        day, month = groups
        return _build_date(day, month, datetime.now().year)
    return None


def _find_dates(text):
    dates = []
    seen = set()
    for pattern, fmt in DATE_PATTERNS:
        for match in pattern.finditer(text):
            parsed = _parse_match(match, fmt)
            if not parsed:
                continue
            key = (parsed.strftime("%Y-%m-%d"), match.start())
            if key in seen:
                continue
            seen.add(key)
            dates.append(
                {
                    "date": parsed,
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "format": fmt,
                }
            )
    return sorted(dates, key=lambda item: item["start"])


def _keyword_distance(context, keywords):
    context_lower = context.lower()
    distances = []
    for keyword in keywords:
        idx = context_lower.rfind(keyword)
        if idx != -1:
            distances.append(len(context_lower) - idx)
    return min(distances) if distances else None


def _score_expiry_candidate(text, candidate):
    before = text[max(0, candidate["start"] - 45) : candidate["start"]]
    after = text[candidate["end"] : min(len(text), candidate["end"] + 25)]
    context = f"{before} {after}"

    score = 0
    exp_distance = _keyword_distance(context, EXP_KEYWORDS)
    mfg_distance = _keyword_distance(context, MFG_KEYWORDS)

    if exp_distance is not None:
        score += max(15, 80 - exp_distance)
    if mfg_distance is not None:
        score -= max(15, 70 - mfg_distance)
    if candidate["format"] in ("my", "text_my"):
        score -= 5

    return score


def _repair_ocr_year(date_value):
    today = datetime.now()
    days_from_today = (date_value - today).days

    if days_from_today > 400 and date_value.year - today.year == 2:
        try:
            return date_value.replace(year=today.year)
        except ValueError:
            return date_value

    if days_from_today < -365 and today.year - date_value.year == 2:
        try:
            return date_value.replace(year=today.year)
        except ValueError:
            return date_value

    return date_value


def parse_date(text):
    if not text:
        return None, "", "none"

    clean_text = _normalize_ocr_date_noise(text)
    dates = _find_dates(clean_text)
    if not dates:
        return None, "", "none"

    scored = [(candidate, _score_expiry_candidate(clean_text, candidate)) for candidate in dates]
    keyword_matches = [item for item in scored if item[1] > 0]

    if keyword_matches:
        best, _score = max(keyword_matches, key=lambda item: (item[1], item[0]["date"]))
        method = "keyword_guided"
    else:
        best = max(dates, key=lambda item: item["date"])
        method = "chronological_fallback" if len(dates) > 1 else "pattern_scan"

    repaired_date = _repair_ocr_year(best["date"])
    return repaired_date.strftime("%Y-%m-%d"), best["match"], method
