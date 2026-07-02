
"""
Enhanced OCR Pipeline
Combines preprocessing, OCR, and date extraction for maximum accuracy
Works with or without API keys
"""

import cv2
import numpy as np
import logging
import os
import tempfile
import sys
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

# Reconfigure standard output/error to use UTF-8 to handle unicode progress bars (e.g. EasyOCR model downloads)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.services.enhanced_preprocessing import preprocess_for_ocr, get_ocr_views
from app.services.standalone_date_extractor import extract_dates_standalone, ExtractedDates

logger = logging.getLogger(__name__)


@dataclass
class OCRPipelineResult:
    mfg_date: Optional[str] = None
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    ingredients: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    mrp: Optional[float] = None
    weight: Optional[str] = None
    confidence: float = 0.0
    raw_text: str = ""
    used_vision_llm: bool = False
    success: bool = False


class EnhancedOCRPipeline:
    """
    Enhanced OCR pipeline that uses multiple preprocessed views and extraction methods
    """
    
    def __init__(self):
        self._easyocr_reader = None
        self._paddleocr_available = False
        
        # Try to import OCR libraries
        self._init_ocr_libraries()
    
    def _init_ocr_libraries(self):
        """Initialize available OCR libraries"""
        # Try EasyOCR
        try:
            import easyocr
            logger.info("EasyOCR available")
        except ImportError:
            logger.warning("EasyOCR not available")
        
        # Don't try to import PaddleOCR yet—wait until we need it,
        # because it can have numpy version conflicts
    
    def _get_easyocr_reader(self):
        """Lazy-load EasyOCR reader"""
        if self._easyocr_reader is None:
            try:
                import easyocr
                self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
            except Exception as e:
                logger.error(f"Failed to load EasyOCR: {e}")
        return self._easyocr_reader
    
    def process_image(self, image: np.ndarray, image_path: Optional[str] = None) -> OCRPipelineResult:
        """
        Main pipeline: process an image and extract dates
        
        Args:
            image: numpy array image (BGR format from OpenCV)
            image_path: optional path to image file
            
        Returns:
            OCRPipelineResult with extracted information
        """
        result = OCRPipelineResult()
        
        if image is None or image.size == 0:
            logger.error("Empty image provided")
            return result
        
        # Step 1: Try Vision LLM first if API keys available (most accurate)
        vision_result = self._try_vision_llm(image, image_path)
        if vision_result and vision_result.confidence > 0.6:
            logger.info("Vision LLM succeeded, using its results")
            return vision_result
        
        # Step 2: Fallback to enhanced OCR + standalone extractor
        logger.info("Using enhanced OCR pipeline with standalone extractor")
        ocr_result = self._run_enhanced_ocr(image)
        
        if ocr_result:
            result.raw_text = ocr_result.get('raw_text', '')
            extracted = extract_dates_standalone(result.raw_text)
            
            result.mfg_date = extracted.mfg_date
            result.expiry_date = extracted.expiry_date
            result.batch_number = extracted.batch_number
            result.ingredients = extracted.ingredients
            result.confidence = extracted.confidence
            result.success = (result.mfg_date is not None or result.expiry_date is not None)
        
        return result
    
    def _try_vision_llm(self, image: np.ndarray, image_path: Optional[str]) -> Optional[OCRPipelineResult]:
        """Try Vision LLM if API keys are configured"""
        gemini_key = os.environ.get('GEMINI_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        if not gemini_key and not openai_key:
            logger.info("No Vision LLM API keys configured, skipping")
            return None
        
        try:
            from app.services.vision_llm_service import extract_structured_fields_via_llm
            
            if image_path and os.path.exists(image_path):
                vision_result = extract_structured_fields_via_llm(image_path=image_path)
            else:
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                    temp_path = f.name
                    cv2.imwrite(temp_path, image)
                
                try:
                    vision_result = extract_structured_fields_via_llm(image_path=temp_path)
                finally:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            if vision_result:
                result = OCRPipelineResult(
                    mfg_date=vision_result.mfg_date.isoformat() if hasattr(vision_result.mfg_date, 'isoformat') else vision_result.mfg_date,
                    expiry_date=vision_result.expiry_date.isoformat() if hasattr(vision_result.expiry_date, 'isoformat') else vision_result.expiry_date,
                    batch_number=vision_result.batch_number,
                    ingredients=vision_result.ingredients,
                    product_name=vision_result.product_name,
                    category=vision_result.category,
                    mrp=vision_result.mrp,
                    weight=vision_result.weight,
                    confidence=vision_result.confidence_score,
                    used_vision_llm=True,
                    success=True
                )
                return result
        
        except Exception as e:
            logger.error(f"Vision LLM failed: {e}")
        
        return None
    
    def _run_enhanced_ocr(self, image: np.ndarray) -> Optional[Dict]:
        """Run enhanced OCR with multiple preprocessed views"""
        all_texts = []
        best_confidence = 0.0
        
        # Get multiple preprocessed views
        views = get_ocr_views(image)
        
        for i, view in enumerate(views):
            logger.debug(f"Processing OCR view {i+1}/{len(views)}")
            
            # Try OCR on this view
            ocr_result = self._extract_text_from_view(view)
            
            if ocr_result and ocr_result.get('raw_text'):
                all_texts.append(ocr_result['raw_text'])
                if ocr_result.get('confidence', 0) > best_confidence:
                    best_confidence = ocr_result['confidence']
        
        if all_texts:
            # Combine all texts
            combined_text = '\n'.join(all_texts)
            return {
                'raw_text': combined_text,
                'confidence': best_confidence,
                'line_count': len(combined_text.split('\n'))
            }
        
        return None
    
    def _extract_text_from_view(self, image: np.ndarray) -> Optional[Dict]:
        """Extract text from a single image view using available OCR engines"""
        # Try EasyOCR first (usually available)
        try:
            reader = self._get_easyocr_reader()
            if reader:
                results = reader.readtext(image)
                
                if results:
                    texts = []
                    confidences = []
                    for box, text, conf in results:
                        if text.strip():
                            texts.append(text.strip())
                            confidences.append(conf)
                    
                    if texts:
                        return {
                            'raw_text': '\n'.join(texts),
                            'confidence': sum(confidences) / len(confidences) if confidences else 0.0,
                            'line_count': len(texts)
                        }
        except Exception as e:
            logger.debug(f"EasyOCR failed: {e}")
        
        # Try PaddleOCR as alternative
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            result = ocr.ocr(image, cls=True)
            
            if result and result[0]:
                texts = []
                confidences = []
                for line in result[0]:
                    if line and len(line) >= 2:
                        text_info = line[1]
                        if isinstance(text_info, tuple) and len(text_info) >= 2:
                            text, conf = text_info
                            if text.strip():
                                texts.append(text.strip())
                                confidences.append(conf)
                
                if texts:
                    return {
                        'raw_text': '\n'.join(texts),
                        'confidence': sum(confidences) / len(confidences) if confidences else 0.0,
                        'line_count': len(texts)
                    }
        except Exception as e:
            logger.debug(f"PaddleOCR failed: {e}")
        
        return None


def run_enhanced_ocr_pipeline(image: np.ndarray, image_path: Optional[str] = None) -> OCRPipelineResult:
    """
    Convenience function to run the enhanced OCR pipeline
    
    Args:
        image: numpy array image (BGR)
        image_path: optional path to image file
        
    Returns:
        OCRPipelineResult with extracted information
    """
    pipeline = EnhancedOCRPipeline()
    return pipeline.process_image(image, image_path)
