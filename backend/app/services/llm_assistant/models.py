"""
services/llm_assistant/models.py — Pydantic request and response models for the LLM Assistant.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Payload to interact with the natural-language decision explanation engine."""
    inventory_item_id: int
    question: str = Field(..., min_length=1, description="Question explaining optimizer recommendation")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional list of prior conversation turns: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]"
    )


class ChatResponse(BaseModel):
    """Answer response payload from the LLM assistant."""
    answer: str
    model: str
    generated_at: str
    context_version: str = "1.0"
    sources: List[str] = Field(
        default_factory=lambda: ["Financial Decision Engine", "Warehouse Intelligence", "Cost Benefit Optimizer"]
    )
    prompt_version: str = "1.0"

    model_config = ConfigDict(from_attributes=True)


class ExecutiveSummaryResponse(BaseModel):
    """AI summary outcome payload over multiple scoped batches."""
    summary: str
    model: str
    generated_at: str
    context_version: str = "1.0"
    sources: List[str] = Field(
        default_factory=lambda: ["Financial Decision Engine", "Warehouse Intelligence", "Cost Benefit Optimizer"]
    )
    prompt_version: str = "1.0"

    model_config = ConfigDict(from_attributes=True)
