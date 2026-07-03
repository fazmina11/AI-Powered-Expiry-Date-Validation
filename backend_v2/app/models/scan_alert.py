import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

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
