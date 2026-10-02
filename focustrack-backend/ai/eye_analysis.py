"""
Eye openness analysis.

Computes the standard Eye Aspect Ratio (EAR) from FaceMesh eye-ring
landmarks. EAR is a well-established, cheap-to-compute proxy for eye
openness: it stays roughly constant while eyes are open and drops sharply
toward zero when they close, without needing a trained classifier.
"""

from dataclasses import dataclass

import numpy as np

from ai.face_mesh import LEFT_EYE_RING, RIGHT_EYE_RING
from utils.config import EAR_CLOSED_THRESHOLD


@dataclass
class EyeState:
    left_ear: float
    right_ear: float
    avg_ear: float
    eyes_closed: bool


def _ear(landmarks: np.ndarray, ring: list[int]) -> float:
    """Eye Aspect Ratio for one eye: (vertical distances) / (2 * horizontal distance)."""
    p = [landmarks[i][:2] for i in ring]  # [outer, top1, top2, inner, bottom1, bottom2]
    p = np.array(p)

    vertical_1 = np.linalg.norm(p[1] - p[5])
    vertical_2 = np.linalg.norm(p[2] - p[4])
    horizontal = np.linalg.norm(p[0] - p[3])

    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def analyze_eyes(landmarks: np.ndarray, closed_threshold: float = EAR_CLOSED_THRESHOLD) -> EyeState | None:
    """Compute eye openness from normalized FaceMesh landmarks."""
    if landmarks is None or len(landmarks) <= max(LEFT_EYE_RING + RIGHT_EYE_RING):
        return None

    left = _ear(landmarks, LEFT_EYE_RING)
    right = _ear(landmarks, RIGHT_EYE_RING)
    avg = (left + right) / 2.0

    return EyeState(left_ear=left, right_ear=right, avg_ear=avg, eyes_closed=avg < closed_threshold)
