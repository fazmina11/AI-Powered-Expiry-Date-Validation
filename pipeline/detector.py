import os
import cv2
import numpy as np

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
YOLO_CONFIG_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".ultralytics"))
os.makedirs(YOLO_CONFIG_PARENT, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", YOLO_CONFIG_PARENT)

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

# Load model globally to avoid reloading on every request
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'expiry_detector.pt')
try:
    detector_model = YOLO(MODEL_PATH) if YOLO and os.path.exists(MODEL_PATH) else None
except Exception as e:
    detector_model = None
    print(f"Warning: Could not load YOLO model from {MODEL_PATH}. Error: {e}")

def detect_date_region(image_path_or_array):
    """
    Detects the expiry date region in an image using YOLOv8.
    Returns a list of tuples: (x1, y1, x2, y2, confidence)
    """
    if detector_model is None:
        return []

    # Check if input is path or numpy array
    if isinstance(image_path_or_array, str):
        image = cv2.imread(image_path_or_array)
        if image is None:
            raise ValueError(f"Could not read image from {image_path_or_array}")
    else:
        image = image_path_or_array

    try:
        results = detector_model(image, conf=0.05, iou=0.40, max_det=3, verbose=False)
        boxes_out = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                boxes_out.append((x1, y1, x2, y2, conf))
        return boxes_out
    except Exception as e:
        print(f"Error during detection: {e}")
        return []

def crop_date_regions(image_path_or_array, boxes):
    """
    Crops the image based on provided bounding boxes.
    Returns a list of cropped numpy arrays.
    """
    if isinstance(image_path_or_array, str):
        image = cv2.imread(image_path_or_array)
        if image is None:
            raise ValueError(f"Could not read image from {image_path_or_array}")
    else:
        image = image_path_or_array

    crops = []
    for (x1, y1, x2, y2, _) in boxes:
        # Ensure coordinates are within image boundaries
        h, w = image.shape[:2]
        pad_x = max(8, int((x2 - x1) * 0.12))
        pad_y = max(8, int((y2 - y1) * 0.20))
        x1, y1 = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2, y2 = min(w, x2 + pad_x), min(h, y2 + pad_y)
        
        crop = image[y1:y2, x1:x2]
        if crop.size > 0:
            crops.append(crop)
    
    return crops
