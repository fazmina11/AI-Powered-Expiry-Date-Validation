import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExternalProductCache(Base):
    __tablename__ = "external_product_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    query_value = Column(String(255), nullable=False, index=True)
    query_type = Column(String(50), nullable=False, index=True)
    external_source = Column(String(100), nullable=False, default="OPEN_FOOD_FACTS", index=True)
    external_product_id = Column(String(255), nullable=True)
    external_source_url = Column(Text, nullable=True)
    barcode = Column(String(100), nullable=True, index=True)
    product_name = Column(String(255), nullable=True, index=True)
    brand = Column(String(150), nullable=True)
    category = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    nutrition_info = Column(JSONB, nullable=True)
    storage_instruction = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    raw_response = Column(JSONB, nullable=True)
    cache_status = Column(String(50), nullable=False, default="ACTIVE")
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lookup_logs = relationship("ProductLookupLog", back_populates="external_cache")


class ProductLookupLog(Base):
    __tablename__ = "product_lookup_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    query_value = Column(String(255), nullable=False, index=True)
    query_type = Column(String(50), nullable=False, index=True)
    result_status = Column(String(50), nullable=False, index=True)
    result_source = Column(String(100), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    external_cache_id = Column(UUID(as_uuid=True), ForeignKey("external_product_cache.id", ondelete="SET NULL"), nullable=True)
    requested_by = Column(String(150), nullable=True)
    request_source = Column(String(100), nullable=False, default="BACKEND_API")
    telegram_chat_id = Column(String(150), nullable=True)
    telegram_user_id = Column(String(150), nullable=True)
    n8n_execution_id = Column(String(150), nullable=True)
    response_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    lookup_duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    product = relationship("Product", back_populates="lookup_logs")
    external_cache = relationship("ExternalProductCache", back_populates="lookup_logs")


class UnknownProductRequest(Base):
    __tablename__ = "unknown_product_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    query_value = Column(String(255), nullable=False, index=True)
    query_type = Column(String(50), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    product_name = Column(String(255), nullable=True)
    request_source = Column(String(100), nullable=False, default="BACKEND_API")
    requested_by = Column(String(150), nullable=True)
    telegram_chat_id = Column(String(150), nullable=True)
    telegram_user_id = Column(String(150), nullable=True)
    n8n_execution_id = Column(String(150), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    admin_notes = Column(Text, nullable=True)
    resolved_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    resolved_product = relationship("Product", back_populates="resolved_unknown_requests")
