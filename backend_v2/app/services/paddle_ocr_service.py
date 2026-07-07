"""
services/paddle_ocr_service.py
Sprint 3 — Raw OCR text extraction using EasyOCR first for better robustness!

Responsibilities:
    - Load EasyOCR reader exactly once (module-level singleton).
    - If EasyOCR fails, fall back to PaddleOCR.
    - Add image preprocessing to improve OCR results.
    - Expose extract_text(image_path) → {"raw_text": "...", "confidence": 0.91}
"""

from __future__ import annotations

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Singletons ────────────────────────────────────────────────────────────────
_paddle_reader: Optional[any] = None
_easy_reader: Optional[any] = None
_use_easyocr: bool = True  # Default to EasyOCR for better robustness

def _preprocess_image(image_path: str) -> str:
    """
    Apply preprocessing to improve OCR:
    - Resize to reasonable dimensions
    - Enhance contrast/sharpness
    - Convert to grayscale
    - Denoise
    Returns path to preprocessed image
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageEnhance, ImageFilter

        # Load image with OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return image_path
        
        # Resize if too small or too large (max 1920x1080)
        h, w = img.shape[:2]
        max_dim = 1080
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Convert to PIL for easier processing
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.3)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(1.5)
        
        # Apply mild denoising
        pil_img = pil_img.filter(ImageFilter.SMOOTH)
        
        # Save preprocessed image to temp file
        temp_dir = os.path.dirname(image_path)
        filename, ext = os.path.splitext(os.path.basename(image_path))
        preprocessed_path = os.path.join(temp_dir, f"{filename}_preprocessed{ext}")
        pil_img.save(preprocessed_path)
        
        logger.info(f"Preprocessed image saved to: {preprocessed_path}")
        return preprocessed_path
    except Exception as e:
        logger.error(f"Image preprocessing failed, using original: {e}")
        return image_path

def _get_reader():
    """
    Lazy-initialise and return the shared EasyOCR or PaddleOCR Reader.
    """
    global _paddle_reader, _easy_reader, _use_easyocr
    
    if _use_easyocr:
        if _easy_reader is None:
            try:
                import easyocr
                logging.getLogger('easyocr').setLevel(logging.WARNING)
                _easy_reader = easyocr.Reader(['en'], gpu=False)
                logger.info("Successfully loaded EasyOCR reader.")
            except Exception as e:
                logger.error(f"Failed to load EasyOCR: {e}. Falling back to PaddleOCR.")
                _use_easyocr = False
                return _get_reader()
        return _easy_reader

    if _paddle_reader is None:
        try:
            from paddleocr import PaddleOCR
            # Disable noisy logs from paddle
            logging.getLogger('ppocr').setLevel(logging.WARNING)
            
            # Try new/classic PaddleOCR initialization arguments
            try:
                _paddle_reader = PaddleOCR(
                    use_textline_orientation=True,
                    lang='en',
                    device='cpu',
                    enable_mkldnn=False,
                    show_log=False
                )
                logger.info("Successfully initialized PaddleOCR with CPU arguments.")
            except Exception as e:
                logger.debug(f"PaddleOCR new init failed: {e}. Trying classic fallback...")
                try:
                    _paddle_reader = PaddleOCR(
                        use_angle_cls=True,
                        lang='en',
                        use_gpu=False,
                        show_log=False
                    )
                    logger.info("Successfully initialized PaddleOCR with classic arguments.")
                except Exception as e2:
                    logger.debug(f"PaddleOCR classic init failed: {e2}. Trying minimal arguments...")
                    _paddle_reader = PaddleOCR(lang='en', show_log=False)
                    logger.info("Successfully initialized PaddleOCR with minimal arguments.")
        except ImportError:
            logger.error("Neither EasyOCR nor PaddleOCR are installed.")
            raise
        except Exception as exc:
            logger.error(f"Error initializing OCR: {exc}")
            raise
            
    return _paddle_reader


# ── Public API ────────────────────────────────────────────────────────────────

def extract_text(image_path: str) -> dict:
    """
    Run EasyOCR (with PaddleOCR fallback) on a single image and return aggregated raw text.
    """
    image_path = os.path.abspath(image_path)

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Apply preprocessing
    processed_path = _preprocess_image(image_path)
    
    reader = _get_reader()
    
    global _use_easyocr
    if _use_easyocr:
        # EasyOCR processing
        easyocr_path = processed_path.replace("\\", "/")
        results = reader.readtext(easyocr_path)

        if not results:
            return {
                "raw_text":   "",
                "confidence": 0.0,
                "line_count": 0,
                "image_path": image_path,
                "blocks":     [],
            }

        clean_texts: list[str] = []
        clean_scores: list[float] = []
        blocks: list[dict] = []

        for box, text, confidence in results:
            if text.strip():
                clean_texts.append(text.strip())
                clean_scores.append(float(confidence))
                
                try:
                    x_coords = [float(pt[0]) for pt in box]
                    y_coords = [float(pt[1]) for pt in box]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                except Exception:
                    x_min, y_min, x_max, y_max = 0.0, 0.0, 0.0, 0.0

                blocks.append({
                    "text": text.strip(),
                    "confidence": round(float(confidence), 4),
                    "x_min": round(x_min, 1),
                    "y_min": round(y_min, 1),
                    "x_max": round(x_max, 1),
                    "y_max": round(y_max, 1)
                })

        raw_text   = "\n".join(clean_texts)
        confidence = round(sum(clean_scores) / len(clean_scores), 4) if clean_scores else 0.0
        
        # Cleanup preprocessed image
        if processed_path != image_path and os.path.exists(processed_path):
            try:
                os.remove(processed_path)
            except Exception:
                pass

        return {
            "raw_text":   raw_text,
            "confidence": confidence,
            "line_count": len(clean_texts),
            "image_path": image_path,
            "blocks":     blocks,
        }
    else:
        # PaddleOCR processing
        try:
            results = reader.ocr(processed_path, cls=True)
        except TypeError:
            results = reader.ocr(processed_path)

        if not results or not results[0]:
            # Cleanup
            if processed_path != image_path and os.path.exists(processed_path):
                try:
                    os.remove(processed_path)
                except Exception:
                    pass
            return {
                "raw_text":   "",
                "confidence": 0.0,
                "line_count": 0,
                "image_path": image_path,
                "blocks":     [],
            }

        clean_texts: list[str] = []
        clean_scores: list[float] = []
        blocks: list[dict] = []
        
        first_page = results[0]
        if isinstance(first_page, dict):
            # PaddleX format
            rec_texts = first_page.get("rec_texts", [])
            rec_scores = first_page.get("rec_scores", [])
            for text, confidence in zip(rec_texts, rec_scores):
                if text and text.strip():
                    clean_texts.append(text.strip())
                    clean_scores.append(float(confidence))
                    blocks.append({
                        "text": text.strip(),
                        "confidence": round(float(confidence), 4),
                        "x_min": 0.0, "y_min": 0.0, "x_max": 0.0, "y_max": 0.0
                    })
        elif isinstance(first_page, list):
            # Classic format: [[[box_coords], (text, confidence)], ...]
            for line in first_page:
                if line and len(line) >= 2:
                    box = line[0]
                    text, confidence = line[1]
                    if text and text.strip():
                        clean_texts.append(text.strip())
                        clean_scores.append(float(confidence))
                        
                        try:
                            x_coords = [float(pt[0]) for pt in box]
                            y_coords = [float(pt[1]) for pt in box]
                            x_min, x_max = min(x_coords), max(x_coords)
                            y_min, y_max = min(y_coords), max(y_coords)
                        except Exception:
                            x_min, y_min, x_max, y_max = 0.0, 0.0, 0.0, 0.0

                        blocks.append({
                            "text": text.strip(),
                            "confidence": round(float(confidence), 4),
                            "x_min": round(x_min, 1),
                            "y_min": round(y_min, 1),
                            "x_max": round(x_max, 1),
                            "y_max": round(y_max, 1)
                        })

        raw_text   = "\n".join(clean_texts)
        confidence = round(sum(clean_scores) / len(clean_scores), 4) if clean_scores else 0.0
        
        # Cleanup preprocessed image
        if processed_path != image_path and os.path.exists(processed_path):
            try:
                os.remove(processed_path)
            except Exception:
                pass

        return {
            "raw_text":   raw_text,
            "confidence": confidence,
            "line_count": len(clean_texts),
            "image_path": image_path,
            "blocks":     blocks,
        }
