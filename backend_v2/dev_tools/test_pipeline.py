
"""
Test the enhanced OCR pipeline with sample images
"""

import sys
import os
import cv2
import logging

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.enhanced_ocr_pipeline import EnhancedOCRPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sample_text():
    """Test standalone date extraction with sample text"""
    print("\n" + "="*60)
    print("Testing Standalone Date Extractor")
    print("="*60)
    
    from app.services.standalone_date_extractor import extract_dates_standalone
    
    test_cases = [
        "MFG: 15/03/2024  EXP: 15/03/2025  BATCH: ABC123",
        "Manufactured: 03-15-2024  Best Before: 03-15-2026",
        "PKD 15 MAR 2024  USE BY 15 MAR 2025  LOT: XYZ789",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {text}")
        result = extract_dates_standalone(text)
        print(f"  MFG Date: {result.mfg_date}")
        print(f"  EXP Date: {result.expiry_date}")
        print(f"  Batch:    {result.batch_number}")
        print(f"  Confidence: {result.confidence:.2f}")


def test_image(image_path):
    """Test pipeline with an image file"""
    print("\n" + "="*60)
    print(f"Testing with Image: {image_path}")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        return
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print("ERROR: Could not read image")
        return
    
    # Process
    pipeline = EnhancedOCRPipeline()
    result = pipeline.process_image(image, image_path)
    
    print("\nResults:")
    print(f"  Success: {result.success}")
    print(f"  MFG Date: {result.mfg_date}")
    print(f"  EXP Date: {result.expiry_date}")
    print(f"  Batch: {result.batch_number}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Used Vision LLM: {result.used_vision_llm}")
    
    if result.raw_text:
        print(f"\n  Raw OCR Text:\n{result.raw_text}")


def main():
    print("\nEnhanced OCR Pipeline Test Suite")
    print("="*60)
    
    # Test standalone extractor first
    test_sample_text()
    
    # Check if there are sample images
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    sample_images = []
    
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    sample_images.append(os.path.join(root, file))
    
    if sample_images:
        print(f"\nFound {len(sample_images)} sample images")
        for img_path in sample_images[:3]:  # Test first 3
            test_image(img_path)
    else:
        print("\nNo sample images found. To test with images:")
        print("  1. Place images in backend_v2/uploads/")
        print("  2. Or run: python test_pipeline.py path/to/your/image.jpg")
    
    # Test with user-provided image if specified
    if len(sys.argv) > 1:
        test_image(sys.argv[1])
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print("\nTo run the webcam scanner:")
    print("  python webcam_scanner.py")


if __name__ == "__main__":
    main()
