from typing import Any, Optional, List, Dict
from pydantic import BaseModel

class ProductSummary(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    storage_instruction: Optional[str] = None
    manufacturer: Optional[str] = None
    country_of_origin: Optional[str] = None
    image_url: Optional[str] = None
    product_source: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductSearchResponse(BaseModel):
    status: str
    source: Optional[str] = None
    search_type: str
    result_count: int
    query: Optional[str] = None
    message: Optional[str] = None
    suggested_action: Optional[str] = None
    product: Optional[Dict[str, Any]] = None
    products: Optional[List[Dict[str, Any]]] = None
