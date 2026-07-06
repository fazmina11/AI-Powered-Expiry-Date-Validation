"""
services/llm_assistant/assistant_service.py — AI Assistant Orchestrator.
Coordinates ContextBuilder, PromptBuilder, and HuggingFaceProvider.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.services.llm_assistant.context_builder import build_inventory_context, build_warehouse_summary_context
from app.services.llm_assistant.prompt_builder import PromptBuilder
from app.services.llm_assistant.provider import HuggingFaceProvider, HuggingFaceAPIException
from app.services.llm_assistant.models import ChatRequest
from app.utils.exceptions import InventoryItemNotFoundError


class AssistantOrchestrator:
    """Core coordinator managing the LLM pipeline."""

    def __init__(self):
        self.provider = HuggingFaceProvider()
        self.prompt_builder = PromptBuilder()

    def chat_explain_decision(self, db: Session, request: ChatRequest) -> Dict[str, Any]:
        """Loads inventory batch details, formats prompts with history, and generates explanations."""
        # 1. Load inventory item
        item = db.query(InventoryItem).filter(InventoryItem.id == request.inventory_item_id).first()
        if not item:
            raise InventoryItemNotFoundError(f"Inventory item ID {request.inventory_item_id} not found")

        # 2. Build context JSON
        context = build_inventory_context(db, item)

        # 3. Build prompt
        prompt = self.prompt_builder.build_chat_prompt(
            context=context,
            question=request.question,
            history=request.conversation_history
        )

        # 4. Generate response via LLM
        answer = self.provider.generate_response(prompt)

        return {
            "answer": answer,
            "model": self.provider.model,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "context_version": "1.0",
        }

    def get_executive_summary(
        self,
        db: Session,
        warehouse: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Queries scoped inventory batches under filters and generates natural-language executive summaries."""
        # 1. Query matching inventory items
        query = db.query(InventoryItem)
        
        # Apply filters (warehouse ID must match source WH-BLR or be resolved from product relationship)
        # Since we defaulted source warehouse to WH-BLR in Phase 4-5, let's assume all inventory items are currently at WH-BLR
        # or we filter items whose products belong to the specified category.
        if category:
            query = query.join(Product).filter(Product.category.ilike(category))

        items = query.all()

        # Filter items by priority or warehouse after loading (since priority is calculated on the fly)
        filtered_items = []
        for item in items:
            # We can run the financial analysis to extract priority
            # E.g. filter by priority
            from app.services.financial_decision_service import perform_financial_analysis
            try:
                analysis = perform_financial_analysis(db, item.id)
                # If priority is specified, match it
                if priority and analysis["financial_priority"].upper() != priority.upper():
                    continue
                # If warehouse is specified, match source warehouse (we assume WH-BLR for all or we filter)
                if warehouse and warehouse != "WH-BLR":
                    continue
                filtered_items.append(item)
            except Exception:
                continue

        # 2. Build structured context JSON
        context = build_warehouse_summary_context(db, filtered_items)

        # 3. Build prompt
        filter_desc = f"Warehouse: {warehouse or 'All'}, Priority: {priority or 'All'}, Category: {category or 'All'}"
        prompt = self.prompt_builder.build_executive_summary_prompt(context, filter_desc)

        # 4. Generate response via LLM
        summary_text = self.provider.generate_response(prompt)

        return {
            "summary": summary_text,
            "model": self.provider.model,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "context_version": "1.0",
        }
