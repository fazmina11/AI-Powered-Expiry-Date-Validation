"""
services/vision_llm_service.py
Sprint 5 — Dual-mode OCR extraction:
  Mode 1 (Text-LLM)  : PaddleOCR raw text → LLM text parser (cheap, ~100 tokens)
  Mode 2 (Vision-LLM): Raw image bytes   → LLM vision model (accurate, ~1000 tokens)
"""

from __future__ import annotations

import os
import json
import base64
import logging
import mimetypes
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Pydantic Schema ───────────────────────────────────────────────────────────

class StructuredExtractionResult(BaseModel):
    mfg_date: Optional[str] = Field(
        None, description="The manufacturing date in YYYY-MM-DD format."
    )
    expiry_date: Optional[str] = Field(
        None, description="The expiration or best-before date in YYYY-MM-DD format."
    )
    batch_number: Optional[str] = Field(
        None, description="The batch or lot number of the product."
    )
    mrp: Optional[float] = Field(
        None, description="Maximum Retail Price (MRP) value as a float."
    )
    weight: Optional[str] = Field(
        None, description="Net weight or volume (e.g. 500g, 1L, 250ml)."
    )
    product_name: Optional[str] = Field(
        None, description="Estimated brand or name of the product."
    )
    category: Optional[str] = Field(
        None, description="Category of the product (e.g., Dairy, Bakery, Beverages, etc.)."
    )
    ingredients: Optional[str] = Field(
        None, description="The list of ingredients of the product."
    )
    confidence_score: float = Field(
        ..., description="Estimated confidence score of the OCR extraction between 0.0 and 1.0."
    )
    shelf_life_days: Optional[int] = Field(
        None, description="Relative shelf-life in days (e.g. Best before 90 days = 90)."
    )


# ── Vision Prompt Builder ─────────────────────────────────────────────────────

def build_vision_prompt(is_crop: bool) -> str:
    # Guidelines on parsing dates
    date_guidelines = (
        "IMPORTANT FOR DATES:\n"
        "1. The date format on the packaging is typically in DD/MM/YY or DD/MM/YYYY format. "
        "Parse numbers in the order: Day/Month/Year. "
        "For example, '09/03/26' means 9th of March 2026. '08/12/26' means 8th of December 2026. Do NOT parse them as MM/DD/YY.\n"
        "2. If no absolute expiry date is printed but a relative shelf-life is shown (e.g. 'best before 9 months' or 'use within 180 days'), "
        "leave 'expiry_date' as null and set 'shelf_life_days' accordingly (e.g. 9 months = 270 days).\n"
        "3. Output all parsed dates strictly in 'YYYY-MM-DD' format."
    )
    
    if is_crop:
        return (
            "This is a cropped close-up of a product label showing dates, batch, or other text.\n"
            f"{date_guidelines}\n"
            "Extract mfg_date, expiry_date, batch_number, ingredients, category.\n"
            "Return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            "  \"mfg_date\": \"YYYY-MM-DD or null\",\n"
            "  \"expiry_date\": \"YYYY-MM-DD or null\",\n"
            "  \"batch_number\": \"string or null\",\n"
            "  \"mrp\": null,\n"
            "  \"weight\": null,\n"
            "  \"product_name\": null,\n"
            "  \"category\": \"string or null\",\n"
            "  \"ingredients\": \"string or null\",\n"
            "  \"confidence_score\": 0.0,\n"
            "  \"shelf_life_days\": null\n"
            "}\n"
            "Return ONLY the JSON, no markdown, no explanation."
        )
    else:
        return (
            "This is a full product packaging photo.\n"
            f"{date_guidelines}\n"
            "Additional extraction instructions:\n"
            "- Brand and Product Name: Look at the brand logo (e.g. 'Happilo' at the top) and the product description (e.g. 'Dates'). Combine them, e.g. 'Happilo Dates'.\n"
            "- Ingredients: Look for the 'INGREDIENTS:' section (e.g. 'INGREDIENTS: Dates.') and extract it.\n"
            "- Category: Classify the product (e.g. 'Dry Fruits', 'Dairy', 'Snacks', etc.).\n"
            "Return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            "  \"mfg_date\": \"YYYY-MM-DD or null\",\n"
            "  \"expiry_date\": \"YYYY-MM-DD or null\",\n"
            "  \"batch_number\": \"string or null\",\n"
            "  \"mrp\": 0.0,\n"
            "  \"weight\": \"string or null\",\n"
            "  \"product_name\": \"string or null\",\n"
            "  \"category\": \"string or null\",\n"
            "  \"ingredients\": \"string or null\",\n"
            "  \"confidence_score\": 0.0,\n"
            "  \"shelf_life_days\": null\n"
            "}\n"
            "Return ONLY the JSON, no markdown, no explanation."
        )


# ── Internal Providers ────────────────────────────────────────────────────────

def _extract_via_gemini(
    image_bytes: bytes, mime_type: str, api_key: str, is_crop: bool = False
) -> StructuredExtractionResult:
    """Invokes Gemini Vision via REST API (works with all key formats including AQ. keys)."""
    import urllib.request
    import time

    prompt = build_vision_prompt(is_crop)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = json.dumps({
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": image_b64}}
            ]
        }],
        "generationConfig": {"temperature": 0.05}
    }).encode("utf-8")

    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
    last_error = None

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                data = json.loads(text)
                logger.info(f"[VisionLLM] Gemini REST extraction succeeded: model={model_name} attempt={attempt+1}")
                return StructuredExtractionResult.model_validate(data)

            except Exception as e:
                last_error = e
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "RESOURCE_EXHAUSTED" in error_str:
                    wait = min(2 ** attempt * 5, 30)
                    logger.warning(f"[VisionLLM] Rate limit on {model_name} attempt {attempt+1}, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    logger.warning(f"[VisionLLM] {model_name} failed (non-quota): {e}")
                    break

    raise last_error if last_error else RuntimeError("All Gemini models exhausted")


def _extract_via_openai(
    image_bytes: bytes, api_key: str, is_crop: bool = False
) -> StructuredExtractionResult:
    """Invokes OpenAI GPT-4o-mini vision via prompt-driven JSON output."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = build_vision_prompt(is_crop)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        temperature=0.05
    )

    text = response.choices[0].message.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    data = json.loads(text)
    return StructuredExtractionResult.model_validate(data)


# ── Text-Only LLM Parsers (Stage 2: PaddleOCR text → structured JSON) ────────

TEXT_PARSE_PROMPT = (
    "You are an expert at parsing product label text.\n"
    "From the raw OCR text below, extract: mfg_date, expiry_date, batch_number, mrp, weight, product_name, category, ingredients.\n"
    "Convert all dates to strict ISO 8601 YYYY-MM-DD format.\n"
    "IMPORTANT: Dates on the package are typically in DD/MM/YY or DD/MM/YYYY format. Parse them as Day/Month/Year. "
    "For example, '09/03/26' means 9th of March 2026. '08/12/26' means 8th of December 2026.\n"
    "If no absolute expiry date is printed but a relative shelf-life rule is shown (e.g. 'best before 90 days'), "
    "leave 'expiry_date' null and return the parsed duration in days under 'shelf_life_days' (e.g. 90). "
    "Set confidence_score between 0.0 and 1.0 based on how complete and clear the data is.\n\n"
    "RAW OCR TEXT:\n{raw_text}"
)


def _parse_text_via_gemini(raw_text: str, api_key: str) -> StructuredExtractionResult:
    """Send raw OCR text to Gemini via REST API (works with all key formats)."""
    import urllib.request
    import time

    prompt = TEXT_PARSE_PROMPT.format(raw_text=raw_text)
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.05}
    }).encode("utf-8")

    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
    last_error = None

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                data = json.loads(text)
                logger.info(f"[TextLLM] Gemini REST text parse succeeded: model={model_name} attempt={attempt+1}")
                return StructuredExtractionResult.model_validate(data)

            except Exception as e:
                last_error = e
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "RESOURCE_EXHAUSTED" in error_str:
                    wait = min(2 ** attempt * 5, 30)
                    logger.warning(f"[TextLLM] Rate limit on {model_name} attempt {attempt+1}, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    logger.warning(f"[TextLLM] {model_name} failed: {e}")
                    break

    raise last_error if last_error else RuntimeError("All Gemini models exhausted")


def _parse_text_via_openai(raw_text: str, api_key: str) -> StructuredExtractionResult:
    """Send raw OCR text to OpenAI via prompt-driven JSON output."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at parsing product label text. "
                    "Extract structured date fields and return ONLY a JSON object. "
                    "Convert all dates to YYYY-MM-DD. "
                    "Compute expiry from mfg_date if a relative phrase is used. "
                    "Return ONLY the JSON, no markdown."
                )
            },
            {"role": "user", "content": f"RAW OCR TEXT:\n{raw_text}"}
        ],
        temperature=0.05
    )

    text = response.choices[0].message.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    data = json.loads(text)
    return StructuredExtractionResult.model_validate(data)


def _parse_text_via_huggingface(raw_text: str, api_key: str) -> StructuredExtractionResult:
    """Send raw OCR text to Hugging Face Inference API to get structured JSON fields."""
    import requests
    import json
    
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    prompt = (
        f"<|im_start|>system\nYou are an expert assistant that extracts structured fields from raw OCR text. "
        f"You must return ONLY a JSON object in this exact schema, with no markdown block, no explanation:\n"
        f"{{\n"
        f"  \"mfg_date\": \"YYYY-MM-DD or null\",\n"
        f"  \"expiry_date\": \"YYYY-MM-DD or null\",\n"
        f"  \"batch_number\": \"string or null\",\n"
        f"  \"mrp\": 0.0 or null,\n"
        f"  \"weight\": \"string or null\",\n"
        f"  \"product_name\": \"string or null\",\n"
        f"  \"category\": \"string or null\",\n"
        f"  \"ingredients\": \"string or null\",\n"
        f"  \"confidence_score\": 0.9\n"
        f"}}\n"
        f"Convert dates to YYYY-MM-DD. Dates are DD/MM/YY or DD/MM/YYYY. For example, '09/03/26' is 2026-03-09.<|im_end|>\n"
        f"<|im_start|>user\nRAW OCR TEXT:\n{raw_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.1
        }
    }
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"HuggingFace API failed: {response.text}")
        
    res_data = response.json()
    generated_text = ""
    if isinstance(res_data, list) and len(res_data) > 0:
        generated_text = res_data[0].get("generated_text", "")
    elif isinstance(res_data, dict):
        generated_text = res_data.get("generated_text", "")
        
    # Clean up markdown code blocks if any
    cleaned = generated_text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    return StructuredExtractionResult.model_validate(data)
def is_valid_gemini_key(key: Optional[str]) -> bool:
    if not key:
        return False
    key = key.strip()
    return (key.startswith("AIzaSy") or key.startswith("AQ.")) and len(key) >= 20

def is_valid_openai_key(key: Optional[str]) -> bool:
    if not key:
        return False
    key = key.strip()
    return key.startswith("sk-") and len(key) >= 20

def is_valid_hf_key(key: Optional[str]) -> bool:
    if not key:
        return False
    key = key.strip()
    return key.startswith("hf_") and len(key) >= 20


# ── Public API ────────────────────────────────────────────────────────────────

def extract_structured_fields_via_llm(
    image_path: str = None,
    image_b64: str = None,
    is_crop: bool = False
) -> Optional[StructuredExtractionResult]:
    """
    Send an image (either via file path or raw base64 data) to the configured LLM API.
    Returns StructuredExtractionResult, or None if no keys are configured.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not is_valid_gemini_key(gemini_key):
        gemini_key = None
    if not is_valid_openai_key(openai_key):
        openai_key = None

    if not gemini_key and not openai_key:
        logger.info("[VisionLLM] No valid API keys configured. Skipping Vision LLM.")
        return None

    # Load image bytes from path or base64
    if image_b64:
        image_bytes = base64.b64decode(image_b64)
        mime_type = "image/jpeg"
    elif image_path:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
    else:
        logger.warning("[VisionLLM] No image_path or image_b64 provided.")
        return None

    try:
        if gemini_key:
            logger.info("[VisionLLM] Extracting fields via Google Gemini API (is_crop=%s)...", is_crop)
            return _extract_via_gemini(image_bytes, mime_type, gemini_key, is_crop)
        elif openai_key:
            logger.info("[VisionLLM] Extracting fields via OpenAI GPT API (is_crop=%s)...", is_crop)
            return _extract_via_openai(image_bytes, openai_key, is_crop)
    except Exception as exc:
        logger.error("[VisionLLM] External API call failed: %s", exc, exc_info=True)
        return None

    return None


def extract_structured_fields_from_text(
    raw_text: str,
) -> Optional[StructuredExtractionResult]:
    """
    Stage 2 of the combined pipeline:
    Accepts raw OCR text (from local PaddleOCR) and sends it to the LLM
    as a cheap text-only call (~100 tokens) to get structured date output.

    Returns None if no API keys are configured or the call fails.
    """
    if not raw_text or not raw_text.strip():
        logger.info("[TextLLM] Empty raw_text. Skipping text parse.")
        return None

    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")

    if not is_valid_gemini_key(gemini_key):
        gemini_key = None
    if not is_valid_openai_key(openai_key):
        openai_key = None
    if not is_valid_hf_key(hf_key):
        hf_key = None

    if not gemini_key and not openai_key and not hf_key:
        logger.info("[TextLLM] No valid API keys configured. Skipping text LLM.")
        return None

    try:
        if gemini_key:
            logger.info("[TextLLM] Parsing OCR text via Gemini text API...")
            return _parse_text_via_gemini(raw_text, gemini_key)
        elif openai_key:
            logger.info("[TextLLM] Parsing OCR text via OpenAI text API...")
            return _parse_text_via_openai(raw_text, openai_key)
        elif hf_key:
            logger.info("[TextLLM] Parsing OCR text via Hugging Face Inference API...")
            return _parse_text_via_huggingface(raw_text, hf_key)
    except Exception as exc:
        logger.error("[TextLLM] Text LLM parse failed: %s", exc, exc_info=True)
        return None

    return None
