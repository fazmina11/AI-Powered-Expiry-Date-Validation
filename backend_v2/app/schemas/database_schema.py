from datetime import date
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    barcode_type: str = "EAN13"
    category: Optional[str] = None
    sub_category: Optional[str] = None
    description: Optional[str] = None
    net_quantity: Optional[str] = None
    unit: Optional[str] = None
    mrp: Optional[float] = None
    currency: str = "INR"
    country_of_origin: Optional[str] = None
    product_type: Optional[str] = None
    default_storage_type: Optional[str] = None
    shelf_life_label: Optional[str] = None
    product_image_url: Optional[str] = None
    is_perishable: bool = False


class ProductIdentifierCreate(BaseModel):
    product_id: UUID
    identifier_value: str
    identifier_type: str = "EAN13"
    is_primary: bool = True


class ProductIngredientCreate(BaseModel):
    product_id: UUID
    ingredient_name: str
    ingredient_order: Optional[int] = None
    percentage: Optional[float] = None
    is_additive: bool = False
    additive_code: Optional[str] = None


class ProductAllergenCreate(BaseModel):
    product_id: UUID
    allergen_name: str
    allergen_type: Optional[str] = None
    contains: bool = True
    may_contain: bool = False
    source_text: Optional[str] = None


class ProductNutritionCreate(BaseModel):
    product_id: UUID
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    sugar_g: Optional[float] = None
    fat_g: Optional[float] = None
    saturated_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    fiber_g: Optional[float] = None
    raw_nutrition_text: Optional[str] = None


class ProductStorageRequirementCreate(BaseModel):
    product_id: UUID
    storage_type: str
    min_temperature_c: Optional[float] = None
    max_temperature_c: Optional[float] = None
    humidity_notes: Optional[str] = None
    handling_notes: Optional[str] = None


class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class WarehouseCreate(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None


class StorageLocationCreate(BaseModel):
    warehouse_id: UUID
    location_code: str
    zone: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    storage_type: Optional[str] = None


class ScanSessionCreate(BaseModel):
    session_status: str = "IN_PROGRESS"
    operator_name: Optional[str] = None
    device_id: Optional[str] = None
    notes: Optional[str] = None


class BarcodeScanCreate(BaseModel):
    product_id: Optional[UUID] = None
    scan_session_id: Optional[UUID] = None
    raw_barcode: str
    barcode_type: Optional[str] = None
    scan_source: Optional[str] = None
    scan_status: str = "unresolved"
    notes: Optional[str] = None


class ProductImageCreate(BaseModel):
    product_id: UUID
    scan_session_id: Optional[UUID] = None
    file_path: str
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    image_type: Optional[str] = None
    processing_status: str = "uploaded"
    notes: Optional[str] = None


class OCRResultCreate(BaseModel):
    product_id: Optional[UUID] = None
    scan_session_id: Optional[UUID] = None
    product_image_id: UUID
    inventory_item_id: Optional[UUID] = None
    raw_text: Optional[str] = None
    ocr_engine: Optional[str] = None
    ocr_engine_version: Optional[str] = None
    ocr_confidence: Optional[float] = None
    overall_confidence: Optional[float] = None
    extracted_product_name: Optional[str] = None
    extracted_brand: Optional[str] = None
    extracted_description: Optional[str] = None
    extracted_ingredients_text: Optional[str] = None
    extracted_nutrition_text: Optional[str] = None
    candidate_mfg_date: Optional[date] = None
    candidate_expiry_date: Optional[date] = None
    candidate_packed_date: Optional[date] = None
    best_before_text: Optional[str] = None
    batch_number_detected: Optional[str] = None
    mrp_detected: Optional[float] = None
    date_parse_confidence: Optional[float] = None
    extracted_text_blocks: Optional[list[dict[str, Any]]] = None
    response_json: Optional[dict[str, Any]] = None
    ocr_status: str = "PENDING"


class InventoryItemCreate(BaseModel):
    product_id: UUID
    barcode_scan_id: Optional[UUID] = None
    scan_session_id: Optional[UUID] = None
    ocr_result_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    storage_location_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    packed_date: Optional[date] = None
    quantity: int = 1
    unit: Optional[str] = None
    intake_source: str = "OCR_SCAN"
    intake_status: str = "DATA_INCOMPLETE"
    pipeline_status: str = "PENDING_OCR"
    operator_decision: Optional[str] = None
    notes: Optional[str] = None


class InventoryMovementCreate(BaseModel):
    inventory_item_id: UUID
    from_location_id: Optional[UUID] = None
    to_location_id: Optional[UUID] = None
    movement_type: str
    quantity: int = 1
    reason: Optional[str] = None
    moved_by: Optional[str] = None


class ManualReviewCreate(BaseModel):
    scan_session_id: Optional[UUID] = None
    inventory_item_id: Optional[UUID] = None
    ocr_result_id: Optional[UUID] = None
    review_type: str = "OCR_CORRECTION"
    original_mfg_date: Optional[date] = None
    original_expiry_date: Optional[date] = None
    corrected_mfg_date: Optional[date] = None
    corrected_expiry_date: Optional[date] = None
    corrected_batch_number: Optional[str] = None
    corrected_description: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_note: Optional[str] = None
    review_status: str = "PENDING"


class ScanAlertCreate(BaseModel):
    scan_session_id: Optional[UUID] = None
    inventory_item_id: Optional[UUID] = None
    alert_type: str
    severity: str = "WARNING"
    field_name: Optional[str] = None
    message: str


class AuditLogCreate(BaseModel):
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    message: str
    metadata_json: Optional[dict[str, Any]] = None
    actor_name: Optional[str] = None


class ExternalProductEnrichmentLogCreate(BaseModel):
    product_id: Optional[UUID] = None
    barcode_value: str
    provider: str
    request_url: Optional[str] = None
    response_status: str
    response_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
