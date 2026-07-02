
"""
Enhanced Webcam Scanner
Real-time product date extraction from webcam with improved accuracy
"""

import cv2
import sys
import os
import logging
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.enhanced_ocr_pipeline import EnhancedOCRPipeline, OCRPipelineResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# UI Constants
WINDOW_NAME = "Enhanced Product Date Scanner"
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_GRAY = (128, 128, 128)


class WebcamScanner:
    def __init__(self):
        self.pipeline = EnhancedOCRPipeline()
        self.last_result = None
        self.state = "LIVE"  # LIVE, PROCESSING, RESULT
        self.processing_frame = None
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        logger.info("Webcam initialized successfully")
    
    def draw_live_preview(self, frame):
        """Draw live preview with instructions"""
        # Resize frame to fit canvas
        display = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
        
        # Resize and center frame
        frame_resized = cv2.resize(frame, (1024, 576))
        x_offset = (CANVAS_WIDTH - 1024) // 2
        y_offset = (CANVAS_HEIGHT - 576) // 2
        
        display[y_offset:y_offset+576, x_offset:x_offset+1024] = frame_resized
        
        # Draw semi-transparent header
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (CANVAS_WIDTH, 80), COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Title
        cv2.putText(display, "ENHANCED PRODUCT DATE SCANNER", (CANVAS_WIDTH//2 - 250, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_WHITE, 3)
        
        # Instructions
        cv2.rectangle(display, (0, CANVAS_HEIGHT - 60), (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BLACK, -1)
        cv2.putText(display, "Press SPACE to capture | Press Q to quit", 
                    (CANVAS_WIDTH//2 - 220, CANVAS_HEIGHT - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_YELLOW, 2)
        
        return display
    
    def draw_processing(self, frame):
        """Draw processing state"""
        display = self.draw_live_preview(frame)
        
        # Processing overlay
        overlay = display.copy()
        cv2.rectangle(overlay, (CANVAS_WIDTH//2 - 200, CANVAS_HEIGHT//2 - 50), 
                    (CANVAS_WIDTH//2 + 200, CANVAS_HEIGHT//2 + 50), COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.8, display, 0.2, 0, display)
        
        cv2.putText(display, "PROCESSING...", 
                    (CANVAS_WIDTH//2 - 100, CANVAS_HEIGHT//2 + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_GREEN, 3)
        
        return display
    
    def draw_result(self, frame, result: OCRPipelineResult):
        """Draw scan results"""
        display = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
        
        # Resize frame to left side
        frame_resized = cv2.resize(frame, (512, 288))
        display[50:50+288, 50:50+512] = frame_resized
        
        # Title
        cv2.putText(display, "SCAN RESULTS", (650, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_WHITE, 3)
        
        # Draw result fields
        y_pos = 180
        line_height = 60
        
        fields = [
            ("Manufacturing Date:", result.mfg_date),
            ("Expiry Date:", result.expiry_date),
            ("Batch Number:", result.batch_number),
            ("Ingredients:", result.ingredients),
            ("Confidence:", f"{result.confidence:.2f}" if result.confidence else "N/A"),
            ("Used Vision LLM:", "Yes" if result.used_vision_llm else "No"),
        ]
        
        for label, value in fields:
            # Label
            cv2.putText(display, label, (600, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_GRAY, 2)
            
            # Value
            if value:
                color = COLOR_GREEN if (label == "Manufacturing Date:" or label == "Expiry Date:") else COLOR_WHITE
                # Truncate ingredients if too long to prevent overflowing screen
                val_str = value
                if label == "Ingredients:" and len(value) > 40:
                    val_str = value[:37] + "..."
                cv2.putText(display, val_str, (600, y_pos + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            else:
                cv2.putText(display, "Not Detected", (600, y_pos + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLOR_RED, 2)
            
            y_pos += line_height
        
        # Status
        status_text = "SUCCESS" if result.success else "FAILED"
        status_color = COLOR_GREEN if result.success else COLOR_RED
        cv2.putText(display, f"Status: {status_text}", (600, y_pos + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3)
        
        # Instructions at bottom
        cv2.rectangle(display, (0, CANVAS_HEIGHT - 60), (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BLACK, -1)
        cv2.putText(display, "Press SPACE to scan again | Press Q to quit", 
                    (CANVAS_WIDTH//2 - 250, CANVAS_HEIGHT - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_YELLOW, 2)
        
        return display
    
    def run(self):
        """Main scanner loop"""
        logger.info("Starting webcam scanner...")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Could not read frame from webcam")
                    continue
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    logger.info("Quit signal received")
                    break
                
                if self.state == "LIVE":
                    display = self.draw_live_preview(frame)
                    
                    if key == ord(' '):
                        self.state = "PROCESSING"
                        self.processing_frame = frame.copy()
                
                elif self.state == "PROCESSING":
                    display = self.draw_processing(self.processing_frame)
                    cv2.imshow(WINDOW_NAME, display)
                    cv2.waitKey(1)  # Update display
                    
                    # Process the image
                    logger.info("Processing captured image...")
                    try:
                        self.last_result = self.pipeline.process_image(self.processing_frame)
                        logger.info(f"Processing complete: MFG=%s, EXP=%s, Confidence=%.2f", 
                                    self.last_result.mfg_date, 
                                    self.last_result.expiry_date, 
                                    self.last_result.confidence)
                    except Exception as e:
                        logger.error(f"Processing failed: {e}")
                        self.last_result = OCRPipelineResult()
                    
                    self.state = "RESULT"
                
                elif self.state == "RESULT":
                    display = self.draw_result(self.processing_frame, self.last_result)
                    
                    if key == ord(' '):
                        self.state = "LIVE"
                        self.last_result = None
                
                cv2.imshow(WINDOW_NAME, display)
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            for _ in range(5):
                cv2.waitKey(1)


def main():
    """Main function"""
    print("=" * 60)
    print("ENHANCED PRODUCT DATE SCANNER")
    print("=" * 60)
    print("\nInstructions:")
    print("- Position product in front of camera")
    print("- Press SPACE to capture and process")
    print("- Press Q to quit\n")
    
    try:
        scanner = WebcamScanner()
        scanner.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\nError: {e}")
        print("\nPlease make sure:")
        print("1. Webcam is connected and working")
        print("2. Required packages are installed")
        print("3. You have the necessary permissions\n")


if __name__ == "__main__":
    main()
