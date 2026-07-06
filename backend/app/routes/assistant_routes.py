"""
routes/assistant_routes.py — REST API routes for AI Warehouse Financial Assistant.
Mounted under /api/v1/assistant.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.llm_assistant.models import ChatRequest, ChatResponse, ExecutiveSummaryResponse
from app.services.llm_assistant.assistant_service import AssistantOrchestrator
from app.services.llm_assistant.provider import HuggingFaceAPIException
from app.utils.exceptions import InventoryItemNotFoundError
from app.utils.response import error_response

router = APIRouter()
orchestrator = AssistantOrchestrator()


# ── POST /api/v1/assistant/chat ────────────────────────────────

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def assistant_chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Provides natural-language explanations of optimization decisions for a specific inventory batch."""
    try:
        chat_res = orchestrator.chat_explain_decision(db, request)
        return ChatResponse(**chat_res)
    except InventoryItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(str(exc), exc.error_code),
        )
    except HuggingFaceAPIException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(str(exc), "LLM_PROVIDER_ERROR"),
        )


# ── GET /api/v1/assistant/executive-summary ────────────────────

@router.get("/executive-summary", response_model=ExecutiveSummaryResponse, status_code=status.HTTP_200_OK)
def assistant_executive_summary_endpoint(
    warehouse_id: Optional[str] = Query(default=None, alias="warehouse"),
    priority: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Provides an AI-generated natural-language executive summary over high-risk batches within a filtered scope."""
    try:
        summary_res = orchestrator.get_executive_summary(
            db,
            warehouse=warehouse_id,
            priority=priority,
            category=category,
        )
        return ExecutiveSummaryResponse(
            summary=summary_res["summary"],
            model=summary_res["model"],
            generated_at=summary_res["generated_at"],
            context_version=summary_res["context_version"],
        )
    except HuggingFaceAPIException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(str(exc), "LLM_PROVIDER_ERROR"),
        )
