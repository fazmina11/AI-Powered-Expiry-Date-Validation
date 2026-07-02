import os
import time
import cv2
import numpy as np

def save_label_image(frame: np.ndarray, upload_dir: str = "./uploads/labels") -> str:
    """
    Saves an image frame to the local filesystem and returns the absolute path.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Cannot save an empty frame.")
        
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{int(time.time() * 1000)}.jpg"
    filepath = os.path.join(upload_dir, filename)
    
    success = cv2.imwrite(filepath, frame)
    if not success:
        raise OSError(f"Failed to write image frame to disk at: {filepath}")
        
    return os.path.abspath(filepath)
