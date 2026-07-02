import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.database import Base


class ProductQuestionLog(Base):
    __tablename__ = "product_question_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question = Column(Text, nullable=False)
    detected_intent = Column(String(100), nullable=True, index=True)
    extracted_entity = Column(String(255), nullable=True)
    result_status = Column(String(50), nullable=True)
    result_source = Column(String(100), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True, index=True)
    request_source = Column(String(100), nullable=False, default="BACKEND_API")
    requested_by = Column(String(150), nullable=True)
    telegram_chat_id = Column(String(150), nullable=True)
    telegram_user_id = Column(String(150), nullable=True)
    n8n_execution_id = Column(String(150), nullable=True)
    response_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
