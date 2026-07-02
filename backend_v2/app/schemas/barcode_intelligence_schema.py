from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class BarcodeIntelligence(BaseModel):
    value: str
    barcode_type: str
    length: int
    country_prefix: Optional[str] = None
    country: Optional[str] = None
    manufacturer_code: Optional[str] = None
    product_code: Optional[str] = None
    check_digit: Optional[int] = None
    checksum_valid: bool
    scan_timestamp: datetime
    is_gs1_barcode: bool = False
    gtin: Optional[str] = None
    manufacturing_date: Optional[date] = None  # Proper date field
    expiry_date: Optional[date] = None         # Proper date field
    best_before_date: Optional[date] = None    # Proper date field
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    serial_number: Optional[str] = None
