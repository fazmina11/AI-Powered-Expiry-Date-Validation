"""
services/image_capture_service.py
Sprint 2 — Capture and save product label images from camera frames.

Responsibilities:
    - capture(frame)  → return a clean copy of the current frame
    - save(frame)     → persist frame to uploads/labels/<timestamp>.jpg
                        and return the saved path

NO FastAPI. NO database. NO SQLAlchemy. NO OCR.
"""

from __future__ import annotations

import numpy as np

from app.utils.file_handler import save_label_image


class ImageCaptureService:
    """
    Handles grabbing and persisting a single label image from a live camera frame.

    Usage (inside camera_test.py):
        svc = ImageCaptureService()

        # Take a snapshot of the current frame (in-memory copy)
        snapshot = svc.capture(frame)

        # Persist to disk
        path = svc.save(snapshot)
        print(f"Saved: {path}")
    """

    def capture(self, frame: np.ndarray) -> np.ndarray:
        """
        Return a clean in-memory copy of the given frame.

        This decouples the snapshot from the live camera buffer so the
        caller can continue reading frames while the snapshot is processed.

        Args:
            frame: OpenCV BGR image from VideoCapture.read().

        Returns:
            A deep copy of the frame (safe to modify or save later).

        Raises:
            ValueError: if frame is None or empty.
        """
        if frame is None or frame.size == 0:
            raise ValueError("Cannot capture an empty frame.")
        return frame.copy()

    def save(self, frame: np.ndarray) -> str:
        """
        Save the frame to uploads/labels/<timestamp>.jpg on the local filesystem.

        Args:
            frame: OpenCV BGR image (numpy array).

        Returns:
            Absolute path of the saved JPEG file.

        Raises:
            ValueError: if frame is None or empty.
            OSError:    if writing to disk fails.
        """
        return save_label_image(frame)
