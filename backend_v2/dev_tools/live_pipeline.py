import cv2
import sys
import os
import time
import argparse
import logging
import traceback
import numpy as np
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
)
logger = logging.getLogger("live_pipeline")

# Ensure backend_v2 is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.scan_pipeline_service import ScanPipelineService
from app.services.alert_service import AlertService

# UI Constants
CANVAS_W, CANVAS_H = 1600, 900
BG_COLOR = (20, 20, 20)
TEXT_WHITE = (240, 240, 240)
TEXT_GRAY = (150, 150, 150)
GREEN = (0, 255, 100)
YELLOW = (0, 200, 255)
RED = (0, 50, 255)

class CleanUI:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        
    def reset(self):
        self.canvas[:] = BG_COLOR
        
    def draw_live_preview(self, frame):
        self.reset()
        # Scale camera feed to fit center screen nicely (e.g., 1280x720)
        scaled_frame = cv2.resize(frame, (1280, 720))
        x_offset = (CANVAS_W - 1280) // 2
        y_offset = (CANVAS_H - 720) // 2
        
        self.canvas[y_offset:y_offset+720, x_offset:x_offset+1280] = scaled_frame
        
        # Border
        cv2.rectangle(self.canvas, (x_offset, y_offset), (x_offset+1280, y_offset+720), (100, 100, 100), 2)
        
        # Top Header
        cv2.putText(self.canvas, "AI PRODUCT SCANNER - LIVE PREVIEW", (x_offset, y_offset - 20), self.font, 1.0, TEXT_WHITE, 2)
        
        # Bottom instructions
        cv2.putText(self.canvas, "[SPACE] Capture & Process   |   [Q] Quit", (x_offset, y_offset + 760), self.font, 0.8, YELLOW, 2)

    def draw_processing(self, frame):
        self.draw_live_preview(frame)
        
        # Overlay
        overlay = self.canvas.copy()
        cv2.rectangle(overlay, (400, 350), (1200, 550), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, self.canvas, 0.2, 0, self.canvas)
        
        cv2.rectangle(self.canvas, (400, 350), (1200, 550), GREEN, 3)
        cv2.putText(self.canvas, "RUNNING PIPELINE...", (550, 460), self.font, 1.5, GREEN, 4)

    def _draw_field(self, y, label, value, color=GREEN):
        cv2.putText(self.canvas, label, (300, y), self.font, 0.9, TEXT_GRAY, 2)
        cv2.putText(self.canvas, value, (700, y), self.font, 0.9, color, 2)

    def draw_result(self, result):
        self.reset()
        
        # Header
        cv2.putText(self.canvas, "SCAN RESULT", (300, 80), self.font, 1.5, TEXT_WHITE, 3)
        cv2.line(self.canvas, (300, 110), (1300, 110), TEXT_GRAY, 2)
        
        y = 180
        
        # Product Info
        pname = getattr(result.product, 'name', None) if getattr(result, 'product', None) else None
        brand = getattr(result.product, 'brand', None) if getattr(result, 'product', None) else None
        bc_val = getattr(result.barcode, 'value', None) if getattr(result, 'barcode', None) else None
        
        pname_str = pname if pname else "Unknown Product"
        brand_str = brand if brand else "Unknown Product"
        bc_str = bc_val if bc_val else "Not Detected"
        
        self._draw_field(y, "Product Name:", pname_str, GREEN if pname else YELLOW)
        y += 60
        self._draw_field(y, "Brand:", brand_str, GREEN if brand else YELLOW)
        y += 60
        self._draw_field(y, "Barcode:", bc_str, GREEN if bc_val else YELLOW)
        
        cv2.line(self.canvas, (300, y + 30), (1300, y + 30), (50, 50, 50), 2)
        y += 80
        
        # OCR Dates & Info
        mfg = getattr(result.manufacturing, 'manufacturing_date', None) if getattr(result, 'manufacturing', None) else None
        exp = getattr(result.expiry, 'expiry_date', None) if getattr(result, 'expiry', None) else None
        batch = getattr(result.batch, 'batch_number', None) if getattr(result, 'batch', None) else None
        price = getattr(result.pricing, 'price', None) if getattr(result, 'pricing', None) else None
        
        self._draw_field(y, "Manufacturing Date:", mfg if mfg else "Not Detected", GREEN if mfg else RED)
        y += 60
        self._draw_field(y, "Expiry Date:", exp if exp else "Not Detected", GREEN if exp else RED)
        y += 60
        self._draw_field(y, "Batch Number:", batch if batch else "Not Detected", GREEN if batch else YELLOW)
        y += 60
        price_str = f"{price}" if price else "Not Detected"
        self._draw_field(y, "MRP:", price_str, GREEN if price else YELLOW)
        
        cv2.line(self.canvas, (300, y + 30), (1300, y + 30), (50, 50, 50), 2)
        y += 80
        
        # Validation
        conf = getattr(result.ocr, 'confidence', None) if getattr(result, 'ocr', None) else None
        val_status = getattr(result.validation, 'overall_status', "UNKNOWN") if getattr(result, 'validation', None) else "UNKNOWN"
        
        c_color = GREEN if conf and conf > 0.9 else YELLOW if conf and conf > 0.7 else RED
        v_color = GREEN if val_status == "VALID" else RED if val_status == "ERROR" else YELLOW
        
        conf_str = f"{conf:.2f}" if conf else "Not Detected"
        
        self._draw_field(y, "OCR Confidence:", conf_str, c_color)
        y += 60
        self._draw_field(y, "Overall Status:", val_status, v_color)
        
        # Footer
        cv2.putText(self.canvas, "[SPACE] Scan Next Product   |   [Q] Quit", (CANVAS_W // 2 - 300, CANVAS_H - 50), self.font, 1.0, TEXT_WHITE, 2)


def main():
    parser = argparse.ArgumentParser(description="Clean AI Product Scanner")
    parser.add_argument("--image", type=str, help="Path to static image")
    args = parser.parse_args()

    logger.info("Initializing Pipeline Service...")
    try:
        # ONLY initialize the orchestrator
        pipeline = ScanPipelineService()
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return

    if args.image:
        if not os.path.exists(args.image):
            logger.error(f"Image {args.image} not found.")
            return
        result = pipeline.process_scan(args.image)
        print(result.model_dump_json(indent=2))
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        logger.error("Could not open camera.")
        return

    ui = CleanUI()
    cv2.namedWindow("AI Scanner", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("AI Scanner", CANVAS_W, CANVAS_H)

    STATE_LIVE = 0
    STATE_PROCESSING = 1
    STATE_RESULT = 2
    
    current_state = STATE_LIVE
    final_result = None
    
    capture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "live_captures"))
    os.makedirs(capture_dir, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
            
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        if current_state == STATE_LIVE:
            # Pure live preview. No detection, no processing.
            ui.draw_live_preview(frame)
            cv2.imshow("AI Scanner", ui.canvas)
            
            if key == ord(' '):
                current_state = STATE_PROCESSING

        elif current_state == STATE_PROCESSING:
            # Draw freeze frame and processing overlay
            ui.draw_processing(frame)
            cv2.imshow("AI Scanner", ui.canvas)
            cv2.waitKey(100) # Flush GUI so text appears before blocking pipeline
            
            try:
                # Save frame
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(capture_dir, f"capture_{ts}.jpg")
                cv2.imwrite(save_path, frame)
                
                # Execute FULL pipeline on the saved frame
                logger.info("Executing full scan pipeline...")
                final_result = pipeline.process_scan(save_path)
                logger.info("Pipeline execution complete.")
                
            except Exception as e:
                logger.error(f"Pipeline crashed: {e}")
                logger.error(traceback.format_exc())
                final_result = None
                
            current_state = STATE_RESULT
            
        elif current_state == STATE_RESULT:
            if final_result:
                ui.draw_result(final_result)
            else:
                ui.reset()
                cv2.putText(ui.canvas, "PIPELINE FAILED - CHECK CONSOLE", (300, 400), ui.font, 1.5, RED, 3)
                cv2.putText(ui.canvas, "[SPACE] Try Again", (300, 500), ui.font, 1.0, TEXT_WHITE, 2)
                
            cv2.imshow("AI Scanner", ui.canvas)
            
            if key == ord(' '):
                # Discard result, return to live preview
                final_result = None
                current_state = STATE_LIVE

    cap.release()
    cv2.destroyAllWindows()
    for _ in range(5): cv2.waitKey(1)

if __name__ == "__main__":
    main()
