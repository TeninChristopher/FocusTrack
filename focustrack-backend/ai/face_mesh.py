"""
Face mesh (landmark) extraction.

Runs MediaPipe Face Mesh per detected face crop. Cropping to each detected
face (rather than running mesh on the full classroom frame) keeps landmark
quality high regardless of how many students are in frame or how small
each face is at classroom-camera distance.
"""

import mediapipe as mp
import numpy as np

from ai.face_detection import Detection
from utils.config import FACE_MESH_CONFIDENCE
from utils.logger import get_logger

logger = get_logger(__name__)

_mp_face_mesh = mp.solutions.face_mesh

# Landmark indices used downstream by head_pose.py and eye_analysis.py.
# Index reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
NOSE_TIP = 1
CHIN = 152
LEFT_EYE_LEFT_CORNER = 33
RIGHT_EYE_RIGHT_CORNER = 263
LEFT_MOUTH_CORNER = 61
RIGHT_MOUTH_CORNER = 291

LEFT_EYE_RING = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_RING = [263, 387, 385, 362, 380, 373]


class FaceMeshExtractor:
    """Thin, reusable wrapper around MediaPipe FaceMesh, run per face crop."""

    def __init__(self, min_confidence: float = FACE_MESH_CONFIDENCE):
        self._mesh = _mp_face_mesh.FaceMesh(
            static_image_mode=True,  # each call is an independent crop, not a video stream
            max_num_faces=1,
            refine_landmarks=True,  # includes iris landmarks, improves eye_analysis accuracy
            min_detection_confidence=min_confidence,
        )

    def extract(self, frame_bgr: np.ndarray, detection: Detection) -> np.ndarray | None:
        """Return an (N, 3) array of normalized (x, y, z) landmarks for one face,
        in the coordinate space of the *cropped* face region, or None if mesh
        extraction failed on this crop.
        """
        x1, y1, x2, y2 = detection.bbox
        # Pad the crop slightly so landmarks near the detection box edge (chin, ears) aren't clipped.
        pad_x = int((x2 - x1) * 0.15)
        pad_y = int((y2 - y1) * 0.15)
        height, width = frame_bgr.shape[:2]

        cx1 = max(0, x1 - pad_x)
        cy1 = max(0, y1 - pad_y)
        cx2 = min(width, x2 + pad_x)
        cy2 = min(height, y2 + pad_y)

        crop = frame_bgr[cy1:cy2, cx1:cx2]
        if crop.size == 0:
            return None

        rgb_crop = np.ascontiguousarray(crop[:, :, ::-1])
        rgb_crop.flags.writeable = False
        result = self._mesh.process(rgb_crop)

        if not result.multi_face_landmarks:
            return None

        landmarks = result.multi_face_landmarks[0].landmark
        return np.array([(lm.x, lm.y, lm.z) for lm in landmarks], dtype=np.float64)

    def close(self) -> None:
        self._mesh.close()
