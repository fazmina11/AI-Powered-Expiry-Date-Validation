from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProductLookup(BaseModel):
    found: bool
    source: str
    barcode: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
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
    lookup_time_ms: float = 0.0
    cache_status: str = "MISS"
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)
