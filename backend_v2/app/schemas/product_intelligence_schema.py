from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class ScanInfo(BaseModel):
    scan_id: str
    timestamp: datetime

class BarcodeInfo(BaseModel):
    value: Optional[str] = None
    barcode_type: Optional[str] = None
    length: Optional[int] = None
    country_prefix: Optional[str] = None
    country: Optional[str] = None
    manufacturer_code: Optional[str] = None
    product_code: Optional[str] = None
    check_digit: Optional[int] = None
    checksum_valid: Optional[bool] = None
    supplier_grade: Optional[str] = None  # Request 3

class ProductInfo(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    quantity: Optional[str] = None
    weight: Optional[str] = None
    ingredients: Optional[str] = None
    nutrition: Optional[str] = None
    packaging: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    country_of_sale: Optional[str] = None
    labels: Optional[str] = None
    product_url: Optional[str] = None

class ManufacturingInfo(BaseModel):
    manufacturer_code: Optional[str] = None
    manufacturer_name: Optional[str] = None
    manufacturing_date: Optional[date] = None  # Proper date field (Request 1)

class ExpiryInfo(BaseModel):
    expiry_date: Optional[date] = None         # Proper date field (Request 1)
    best_before_date: Optional[date] = None    # Proper date field (Request 1)
    exp_computed: bool = False

class PricingInfo(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None

class BatchInfo(BaseModel):
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None

class OcrInfo(BaseModel):
    raw_text: Optional[str] = None
    confidence: Optional[float] = None
    detected_fields: Dict[str, Any] = Field(default_factory=dict)

class MetadataInfo(BaseModel):
    source_barcode: Optional[str] = None
    source_product: Optional[str] = None
    source_ocr: bool = False

class LookupMetadata(BaseModel):
    provider: Optional[str] = None
    cache_status: str = "MISS"
    lookup_time_ms: float = 0.0

class ProductIntelligence(BaseModel):
    scan: ScanInfo
    barcode: BarcodeInfo
    product: ProductInfo
    manufacturing: ManufacturingInfo
    expiry: ExpiryInfo
    pricing: PricingInfo
    batch: BatchInfo
    ocr: OcrInfo
    metadata: MetadataInfo
    lookup_metadata: LookupMetadata
