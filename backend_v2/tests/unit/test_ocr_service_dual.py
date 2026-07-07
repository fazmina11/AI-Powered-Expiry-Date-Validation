import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.paddle_ocr_service import _get_reader, extract_text

def test_ocr_reader_fallback():
    # Test that if paddleocr is missing, it sets _use_easyocr flag and falls back to EasyOCR
    with patch('builtins.__import__') as mock_import:
        def side_effect(name, *args, **kwargs):
            if 'paddleocr' in name:
                raise ImportError("No module named 'paddleocr'")
            # Return a dummy mock for easyocr
            mock_module = MagicMock()
            return mock_module
        
        mock_import.side_effect = side_effect
        
        # Reset reader states
        import app.services.paddle_ocr_service as service
        service._paddle_reader = None
        service._easy_reader = None
        service._use_easyocr = False
        
        reader = _get_reader()
        assert service._use_easyocr is True
