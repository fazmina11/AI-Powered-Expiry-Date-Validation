import re
import uuid

def is_uuid(value: str) -> bool:
    try:
        uuid_obj = uuid.UUID(value)
        return str(uuid_obj) == value.lower()
    except ValueError:
        return False

def is_barcode_like(value: str) -> bool:
    if not value.isdigit():
        return False
    # Allowed lengths for EAN-8, UPC-A, EAN-13, ITF-14 etc.
    return len(value) in (8, 12, 13, 14)

def is_sku_like(value: str) -> bool:
    # Looks like an internal SKU, such as AMUL-TAAZA-500ML
    # Typically contains uppercase letters, digits, and hyphens
    if not value:
        return False
    # Basic heuristic: contains at least one hyphen and alphanumeric characters, often uppercase
    return bool(re.match(r'^[A-Z0-9]+(-[A-Z0-9]+)+$', value.upper()))

def clean_query(value: str) -> str:
    if not value:
        return ""
    return value.strip()

def detect_query_type(value: str) -> str:
    cleaned = clean_query(value)
    if not cleaned:
        return "UNKNOWN"
        
    if is_uuid(cleaned):
        return "PRODUCT_ID"
        
    if is_barcode_like(cleaned):
        return "BARCODE"
        
    if is_sku_like(cleaned):
        return "SKU"
        
    return "PRODUCT_NAME"
