"""
Image service.

Owns everything filesystem-related about a single frame's image data:
saving the raw upload, drawing the annotated overlay, saving the
processed image, and deleting the raw file once processing succeeds.
"""

import os
from pathlib import Path

import cv2
import numpy as np

from utils.config import MAX_FRAME_DIMENSION, PROCESSED_DIR, RAW_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

# Status -> BGR color (OpenCV convention), matching the frontend's palette:
# success #22C55E, warning #F59E0B, danger #EF4444.
_STATUS_COLOR_BGR = {
    "Highly Attentive": (94, 197, 34),
    "Partially Attentive": (6, 158, 245),
    "Distracted": (68, 68, 239),
}


def save_raw_image(image_bytes: bytes, filename: str) -> Path:
    """Persist an uploaded frame's raw bytes to uploads/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path


def load_image(path: Path) -> np.ndarray | None:
    """Load an image from disk as a BGR numpy array."""
    image = cv2.imread(str(path))
    if image is None:
        logger.warning("Failed to decode image at %s", path)
    return image


def resize_for_inference(frame: np.ndarray, max_dimension: int = MAX_FRAME_DIMENSION) -> tuple[np.ndarray, float]:
    """Downscale a frame so its longest side is `max_dimension`, for predictable CPU latency.

    Returns (resized_frame, scale_factor) where scale_factor maps resized-frame
    coordinates back to the original frame (multiply to undo the resize).
    """
    height, width = frame.shape[:2]
    longest_side = max(height, width)
    if longest_side <= max_dimension:
        return frame, 1.0

    scale = max_dimension / float(longest_side)
    resized = cv2.resize(frame, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
    return resized, 1.0 / scale


def annotate_frame(frame: np.ndarray, tracked_faces: list[dict]) -> np.ndarray:
    """Draw bounding boxes, IDs, tracking paths, and attention labels onto a copy of `frame`.

    Args:
        frame: original-resolution BGR frame
        tracked_faces: list of dicts, each with:
            track_id, bbox (x1,y1,x2,y2 in original-frame coords), attention_score,
            attention_status, history (list of (x,y) points in original-frame coords)
    """
    annotated = frame.copy()

    for face in tracked_faces:
        x1, y1, x2, y2 = face["bbox"]
        color = _STATUS_COLOR_BGR.get(face["attention_status"], (200, 200, 200))

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        # Tracking path: faint polyline through recent centers.
        history = face.get("history") or []
        if len(history) >= 2:
            pts = np.array(history, dtype=np.int32).reshape(-1, 1, 2)
            cv2.polylines(annotated, [pts], isClosed=False, color=color, thickness=1, lineType=cv2.LINE_AA)

        label = f"ID{face['track_id']:02d}  {face['attention_score']}%"
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_y1 = max(0, y1 - text_h - 8)
        cv2.rectangle(annotated, (x1, label_y1), (x1 + text_w + 8, y1), color, -1)
        cv2.putText(
            annotated, label, (x1 + 4, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA
        )

        status_label = face["attention_status"]
        cv2.putText(
            annotated,
            status_label,
            (x1, y2 + 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    return annotated


def save_processed_image(frame: np.ndarray, filename: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / filename
    cv2.imwrite(str(path), frame)
    return path


def delete_raw_image(path: Path) -> None:
    """Delete a raw upload after successful processing. Raw images are temporary only."""
    try:
        if path.exists():
            os.remove(path)
    except OSError as exc:
        logger.warning("Failed to delete raw image %s: %s", path, exc)
