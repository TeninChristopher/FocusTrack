"""
Face detection.

Wraps MediaPipe's Face Detection solution. Models are bundled with the
`mediapipe` pip package itself (legacy `solutions` API) -- no separate
model download/network access needed at runtime.

NOTE: mediapipe>=0.10.14 removed the `solutions` API in favor of the newer
Tasks API, which requires downloading .task model bundles separately.
requirements.txt pins `mediapipe==0.10.13` specifically to keep the legacy,
self-contained API and avoid that extra dependency.
"""

from dataclasses import dataclass

import mediapipe as mp
import numpy as np

from utils.config import FACE_DETECTION_CONFIDENCE, MAX_FACES
from utils.logger import get_logger

logger = get_logger(__name__)

_mp_face_detection = mp.solutions.face_detection


@dataclass
class Detection:
    """A single detected face, in absolute pixel coordinates of the input frame."""

    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)


class FaceDetector:
    """Thin, reusable wrapper around MediaPipe FaceDetection.

    Instantiated once (in analysis_service) and reused across frames --
    MediaPipe graphs are expensive to construct per-call.
    """

    def __init__(self, min_confidence: float = FACE_DETECTION_CONFIDENCE):
        # model_selection=1 = "full range" model, better for classroom-distance faces
        # than the default short-range (0) model tuned for close-up selfie-style shots.
        self._detector = _mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=min_confidence
        )

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        """Detect faces in a BGR (OpenCV-convention) frame.

        Returns absolute-pixel bounding boxes, clamped to frame bounds.
        """
        height, width = frame_bgr.shape[:2]
        rgb_frame = np.ascontiguousarray(frame_bgr[:, :, ::-1])  # BGR -> RGB, MediaPipe expects RGB + contiguous
        rgb_frame.flags.writeable = False

        result = self._detector.process(rgb_frame)
        if not result.detections:
            return []

        detections: list[Detection] = []
        for det in result.detections[:MAX_FACES]:
            box = det.location_data.relative_bounding_box
            x1 = max(0, int(box.xmin * width))
            y1 = max(0, int(box.ymin * height))
            x2 = min(width, int((box.xmin + box.width) * width))
            y2 = min(height, int((box.ymin + box.height) * height))

            if x2 <= x1 or y2 <= y1:
                continue  # degenerate box, skip

            confidence = det.score[0] if det.score else 0.0
            detections.append(Detection(x1, y1, x2, y2, confidence))

        return detections

    def close(self) -> None:
        self._detector.close()
