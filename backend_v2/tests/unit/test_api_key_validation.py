import pytest
import os
from app.services.vision_llm_service import (
    is_valid_gemini_key,
    is_valid_openai_key,
    is_valid_hf_key,
    extract_structured_fields_from_text,
    extract_structured_fields_via_llm
)

def test_is_valid_gemini_key():
    assert is_valid_gemini_key(None) is False
    assert is_valid_gemini_key("") is False
    assert is_valid_gemini_key("   ") is False
    assert is_valid_gemini_key("AQ.12345678901234567") is False
    assert is_valid_gemini_key("AIzaSy12345678901234") is True
    assert is_valid_gemini_key("AIzaSyTooShort") is False

def test_is_valid_openai_key():
    assert is_valid_openai_key(None) is False
    assert is_valid_openai_key("") is False
    assert is_valid_openai_key("sk-") is False
    assert is_valid_openai_key("sk-12345678901234567") is True
    assert is_valid_openai_key("sk-short") is False

def test_is_valid_hf_key():
    assert is_valid_hf_key(None) is False
    assert is_valid_hf_key("") is False
    assert is_valid_hf_key("hf_") is False
    assert is_valid_hf_key("hf_12345678901234567") is True
    assert is_valid_hf_key("hf_short") is False

def test_extract_structured_fields_from_text_with_invalid_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.placeholder")
    monkeypatch.setenv("OPENAI_API_KEY", "invalid_key")
    monkeypatch.setenv("HUGGINGFACE_API_KEY", "invalid_key")
    
    result = extract_structured_fields_from_text("MFG 10/10/2026 EXP 10/10/2027")
    assert result is None
