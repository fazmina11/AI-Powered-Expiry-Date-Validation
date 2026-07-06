"""
services/llm_assistant/provider.py — Abstraction layer for Hugging Face Inference API.
Handles HTTP POST requests, authentication headers, timeouts, and API failure modes gracefully.
"""

from typing import Dict, Any, Optional
import httpx

from app.config import settings


class HuggingFaceAPIException(Exception):
    """Custom exception representing Hugging Face Inference API errors."""
    pass


class HuggingFaceProvider:
    """Decoupled client wrapper to trigger remote Inference API requests."""
    
    def __init__(self):
        self.model = settings.HF_MODEL
        self.api_url = f"{settings.HF_API_URL}/{self.model}"
        self.token = settings.HF_API_TOKEN
        self.timeout = float(settings.LLM_TIMEOUT)

    def generate_response(self, prompt: str) -> str:
        """Triggers Hugging Face text generation model using config parameters."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": settings.MAX_TOKENS,
                "temperature": float(settings.TEMPERATURE),
                "top_p": float(settings.TOP_P),
                "return_full_text": False
            }
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                
                # Check for standard errors
                if response.status_code != 200:
                    raise HuggingFaceAPIException(
                        f"Hugging Face API returned error status {response.status_code}: {response.text}"
                    )
                
                res_data = response.json()
                
                # Hugging Face usually returns a list of items with generated_text
                if isinstance(res_data, list) and len(res_data) > 0:
                    return res_data[0].get("generated_text", "").strip()
                elif isinstance(res_data, dict):
                    return res_data.get("generated_text", "").strip()
                
                return str(res_data).strip()

        except httpx.TimeoutException as exc:
            raise HuggingFaceAPIException(f"LLM request timed out after {self.timeout} seconds.") from exc
        except httpx.RequestError as exc:
            raise HuggingFaceAPIException(f"Network error calling Hugging Face API: {exc}") from exc
        except Exception as exc:
            raise HuggingFaceAPIException(f"Unexpected error executing LLM generation: {exc}") from exc
