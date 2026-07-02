import re


BARCODE_LENGTHS = {8, 12, 13, 14}


def clean_question(question: str) -> str:
    if not question:
        return ""
    return re.sub(r"\s+", " ", question).strip()


def is_question_valid(question: str) -> bool:
    return bool(clean_question(question))


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def detect_question_intent(question: str) -> str:
    text = clean_question(question).lower()
    if not text:
        return "UNKNOWN"

    status_phrases = (
        "is this product expired",
        "is it expired",
        "is product expired",
        "can i stock",
        "ready for stocking",
        "safe to stock",
        "usable",
        "status",
    )
    if _contains_any(text, status_phrases) or re.search(r"\bis\b.+\bexpired\b", text):
        return "PRODUCT_STATUS"

    if _contains_any(text, ("expiry", "expire", "expired", "best before", "use by", "valid till")):
        return "EXPIRY_DATE"

    if _contains_any(text, ("mfg", "manufacturing", "manufacture", "manufactured", "made on", "packed on", "pack date")):
        return "MFG_DATE"

    if _contains_any(text, ("batch", "batch number", "lot", "lot number")):
        return "BATCH_NUMBER"

    if _contains_any(text, ("ingredient", "ingredients", "contains", "composition")):
        return "INGREDIENTS"

    if _contains_any(text, ("nutrition", "nutritional", "calorie", "calories", "energy", "protein", "fat", "carbohydrate", "sugar", "salt", "sodium")):
        return "NUTRITION"

    if _contains_any(text, ("storage", "store", "stored", "keep", "temperature", "refrigerated", "cool dry place")):
        return "STORAGE_INSTRUCTION"

    if _contains_any(text, ("details", "info", "information", "show product", "product details", "about")):
        return "PRODUCT_DETAILS"

    return "UNKNOWN"


def _barcode_token(question: str) -> str | None:
    for token in re.findall(r"\b\d+\b", question):
        if len(token) in BARCODE_LENGTHS:
            return token
    return None


def _sku_token(question: str) -> str | None:
    for token in re.findall(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b", question):
        if re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+", token):
            return token.upper()
    return None


def extract_product_entity(question: str, intent: str) -> str | None:
    cleaned = clean_question(question)
    if not cleaned:
        return None

    barcode = _barcode_token(cleaned)
    if barcode:
        return barcode

    sku = _sku_token(cleaned)
    if sku:
        return sku

    entity = cleaned
    removal_patterns = (
        r"\bwhat\s+is\b",
        r"\bwhat\s+are\b",
        r"\bwhen\s+does\b",
        r"\bhow\s+should\s+i\b",
        r"\bcan\s+i\b",
        r"\bis\s+this\b",
        r"\bis\s+it\b",
        r"\bis\b",
        r"\bshow\b",
        r"\bgive\b",
        r"\btell\s+me\b",
        r"\bplease\b",
        r"\bexpiry\s+date\b",
        r"\bmanufacturing\s+date\b",
        r"\bmfg\s+date\b",
        r"\bbatch\s+number\b",
        r"\bstorage\s+instruction\b",
        r"\bproduct\s+details\b",
        r"\bdetails\b",
        r"\binformation\b",
        r"\bingredients?\b",
        r"\bnutrition(?:al)?\b",
        r"\bstorage\b",
        r"\binstruction\b",
        r"\bstore\b",
        r"\bexpire(?:d|s)?\b",
        r"\bbest\s+before\b",
        r"\buse\s+by\b",
        r"\bvalid\s+till\b",
        r"\bbatch\b",
        r"\blot\b",
        r"\bof\b",
        r"\bfor\b",
        r"\bthe\b",
        r"\bthis\s+product\b",
        r"\bproduct\b",
        r"\?",
    )
    for pattern in removal_patterns:
        entity = re.sub(pattern, " ", entity, flags=re.IGNORECASE)

    entity = re.sub(r"\s+", " ", entity).strip(" .,:;-")
    return entity or None
