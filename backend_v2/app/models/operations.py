import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    contact_name = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    inventory_items = relationship("InventoryItem", back_populates="supplier")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True, unique=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    storage_locations = relationship("StorageLocation", back_populates="warehouse", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="warehouse")


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    location_code = Column(String(100), nullable=False, index=True)
    zone = Column(String(100), nullable=True)
    aisle = Column(String(50), nullable=True)
    rack = Column(String(50), nullable=True)
    shelf = Column(String(50), nullable=True)
    bin = Column(String(50), nullable=True)
    storage_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    warehouse = relationship("Warehouse", back_populates="storage_locations")
    inventory_items = relationship("InventoryItem", back_populates="storage_location")
    movements_from = relationship("InventoryMovement", foreign_keys="InventoryMovement.from_location_id", back_populates="from_location")
    movements_to = relationship("InventoryMovement", foreign_keys="InventoryMovement.to_location_id", back_populates="to_location")


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_status = Column(String(50), nullable=False, default="IN_PROGRESS", index=True)
    operator_name = Column(String(150), nullable=True)
    device_id = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    barcode_scans = relationship("BarcodeScan", back_populates="scan_session")
    product_images = relationship("ProductImage", back_populates="scan_session")
    ocr_results = relationship("OCRResult", back_populates="scan_session")
    inventory_items = relationship("InventoryItem", back_populates="scan_session")
    manual_reviews = relationship("ManualReview", back_populates="scan_session")
    scan_alerts = relationship("ScanAlert", back_populates="scan_session")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    from_location_id = Column(UUID(as_uuid=True), ForeignKey("storage_locations.id", ondelete="SET NULL"), nullable=True)
    to_location_id = Column(UUID(as_uuid=True), ForeignKey("storage_locations.id", ondelete="SET NULL"), nullable=True)
    movement_type = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    reason = Column(Text, nullable=True)
    moved_by = Column(String(100), nullable=True)
    moved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inventory_item = relationship("InventoryItem", back_populates="movements")
    from_location = relationship("StorageLocation", foreign_keys=[from_location_id], back_populates="movements_from")
    to_location = relationship("StorageLocation", foreign_keys=[to_location_id], back_populates="movements_to")


class ScanAlert(Base):
    __tablename__ = "scan_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scan_session_id = Column(UUID(as_uuid=True), ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default="WARNING", index=True)
    field_name = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)
    resolved_by = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    scan_session = relationship("ScanSession", back_populates="scan_alerts")
    inventory_item = relationship("InventoryItem", back_populates="scan_alerts")


class ExternalProductEnrichmentLog(Base):
    __tablename__ = "external_product_enrichment_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    barcode_value = Column(String(150), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    request_url = Column(Text, nullable=True)
    response_status = Column(String(50), nullable=False, index=True)
    response_json = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="enrichment_logs")
