
"""
Enhanced Image Preprocessing Service
Improves OCR accuracy through comprehensive image enhancement techniques
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class EnhancedPreprocessor:
    """
    Comprehensive image preprocessor for OCR enhancement
    """
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """
        Main enhancement pipeline: applies multiple enhancement techniques
        """
        if image is None or image.size == 0:
            return image
            
        # Make a copy to avoid modifying original
        processed = image.copy()
        
        # Step 1: Resize if too small
        processed = EnhancedPreprocessor._resize_if_needed(processed)
        
        # Step 2: Remove glare and reflections
        processed = EnhancedPreprocessor._remove_glare(processed)
        
        # Step 3: Denoise
        processed = EnhancedPreprocessor._denoise_image(processed)
        
        # Step 4: Enhance contrast
        processed = EnhancedPreprocessor._enhance_contrast(processed)
        
        # Step 5: Sharpen
        processed = EnhancedPreprocessor._sharpen_image(processed)
        
        # Step 6: Binarize
        processed = EnhancedPreprocessor._adaptive_binarization(processed)
        
        return processed
    
    @staticmethod
    def _resize_if_needed(image: np.ndarray, min_height: int = 600) -> np.ndarray:
        """Resize image if it's too small for good OCR"""
        h, w = image.shape[:2]
        if h < min_height:
            scale = min_height / h
            new_w = int(w * scale)
            new_h = min_height
            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        return image
    
    @staticmethod
    def _remove_glare(image: np.ndarray) -> np.ndarray:
        """Remove glare and reflections using inpainting"""
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect bright spots (glare)
        _, glare_mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
        
        # Dilate the mask slightly
        kernel = np.ones((3, 3), np.uint8)
        glare_mask = cv2.dilate(glare_mask, kernel, iterations=1)
        
        # Inpaint to remove glare
        if np.sum(glare_mask) > 0:
            if len(image.shape) == 3:
                return cv2.inpaint(image, glare_mask, 3, cv2.INPAINT_TELEA)
            else:
                return cv2.inpaint(image, glare_mask, 3, cv2.INPAINT_TELEA)
        
        return image
    
    @staticmethod
    def _denoise_image(image: np.ndarray) -> np.ndarray:
        """Apply non-local means denoising"""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    @staticmethod
    def _enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE"""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            lab = cv2.merge((l, a, b))
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            return clahe.apply(image)
    
    @staticmethod
    def _sharpen_image(image: np.ndarray) -> np.ndarray:
        """Sharpen image using unsharp masking"""
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        return cv2.addWeighted(image, 2.0, gaussian, -1.0, 0)
    
    @staticmethod
    def _adaptive_binarization(image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding for better text/background separation"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Try multiple binarization methods
        binary1 = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 15
        )
        
        binary2 = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 31, 15
        )
        
        # Combine results - take the one with more text pixels
        text1 = np.sum(binary1 < 128)
        text2 = np.sum(binary2 < 128)
        
        best_binary = binary1 if text1 > text2 else binary2
        
        # Clean up with morphology
        kernel = np.ones((1, 1), np.uint8)
        best_binary = cv2.morphologyEx(best_binary, cv2.MORPH_CLOSE, kernel)
        
        return best_binary
    
    @staticmethod
    def get_multiple_views(image: np.ndarray) -> list[np.ndarray]:
        """
        Generate multiple preprocessed views of the image to increase OCR success
        """
        views = []
        
        # Original enhanced
        views.append(EnhancedPreprocessor.enhance_image(image))
        
        # Slightly rotated variants (±2 degrees) to handle skew
        for angle in [-2, 2]:
            rotated = EnhancedPreprocessor._rotate_image(image, angle)
            views.append(EnhancedPreprocessor.enhance_image(rotated))
        
        # Different contrast levels
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe_strong = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        l_strong = clahe_strong.apply(l)
        lab_strong = cv2.merge((l_strong, a, b))
        contrast_strong = cv2.cvtColor(lab_strong, cv2.COLOR_LAB2BGR)
        views.append(EnhancedPreprocessor.enhance_image(contrast_strong))
        
        return views
    
    @staticmethod
    def _rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image slightly to handle minor skew"""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Convenience function to preprocess an image for OCR
    """
    return EnhancedPreprocessor.enhance_image(image)


def get_ocr_views(image: np.ndarray) -> list[np.ndarray]:
    """
    Get multiple preprocessed views for better OCR coverage
    """
    return EnhancedPreprocessor.get_multiple_views(image)
