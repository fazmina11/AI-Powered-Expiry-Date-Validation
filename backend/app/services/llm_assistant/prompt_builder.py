"""
services/llm_assistant/prompt_builder.py — Dynamic Prompt Template Builder.
Loads raw prompt texts from files and substitutes variables safely.
"""

import json
import os
from typing import Dict, Any, List, Optional


class PromptBuilder:
    """Loads prompt templates dynamically and replaces variables."""

    def __init__(self):
        # backend root directory is parent of app
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.prompts_dir = os.path.join(self.backend_dir, "prompts")


    def _load_template(self, filename: str) -> str:
        """Loads a template file from the prompts directory."""
        filepath = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt template file '{filename}' not found in {self.prompts_dir}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def build_chat_prompt(
        self,
        context: Dict[str, Any],
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Loads system rules and constructs a conversational instruction prompt."""
        system_rules = self._load_template("warehouse_assistant.txt")
        template = self._load_template("decision_explanation.txt")

        # Format history if present
        history_str = "None"
        if history:
            history_lines = []
            for turn in history:
                role = turn.get("role", "user").capitalize()
                content = turn.get("content", "")
                history_lines.append(f"{role}: {content}")
            history_str = "\n".join(history_lines)

        context_json = json.dumps(context, indent=2)
        chat_instruction = template.format(
            context_json=context_json,
            conversation_history=history_str,
            question=question
        )

        # Merge system instructions and user chat turn
        return f"{system_rules}\n\n{chat_instruction}"

    def build_executive_summary_prompt(
        self,
        context: Dict[str, Any],
        filters: str,
    ) -> str:
        """Loads system rules and builds a summary prompt structure."""
        system_rules = self._load_template("warehouse_assistant.txt")
        template = self._load_template("executive_summary.txt")

        context_json = json.dumps(context, indent=2)
        summary_instruction = template.format(
            context_json=context_json,
            filters=filters
        )

        return f"{system_rules}\n\n{summary_instruction}"
