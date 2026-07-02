from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductQuestionRequest(BaseModel):
    question: str = Field(...)
    request_source: Optional[str] = "BACKEND_API"
    requested_by: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_user_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None


class ProductQuestionResponse(BaseModel):
    status: str
    intent: str
    answer_type: str
    answer: str
    data: Optional[dict[str, Any]] = None
