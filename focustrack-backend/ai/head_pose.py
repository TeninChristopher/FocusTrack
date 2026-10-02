"""
Head pose estimation.

Uses OpenCV's solvePnP with a generic 3D face model matched against a
handful of stable MediaPipe FaceMesh landmarks (nose tip, chin, eye
corners, mouth corners) to recover yaw/pitch/roll in degrees. This is the
standard, well-established approach for head pose from 2D face landmarks
without a depth sensor.
"""

from dataclasses import dataclass

import cv2
import numpy as np

from ai.face_mesh import (
    CHIN,
    LEFT_EYE_LEFT_CORNER,
    LEFT_MOUTH_CORNER,
    NOSE_TIP,
    RIGHT_EYE_RIGHT_CORNER,
    RIGHT_MOUTH_CORNER,
)

# Generic 3D face model points (arbitrary units, roughly millimeters),
# in the same order as the 2D landmark indices below.
_MODEL_POINTS_3D = np.array(
    [
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -63.6, -12.5),  # Chin
        (-43.3, 32.7, -26.0),  # Left eye left corner
        (43.3, 32.7, -26.0),  # Right eye right corner
        (-28.9, -28.9, -24.1),  # Left mouth corner
        (28.9, -28.9, -24.1),  # Right mouth corner
    ],
    dtype=np.float64,
)

_LANDMARK_INDICES = [NOSE_TIP, CHIN, LEFT_EYE_LEFT_CORNER, RIGHT_EYE_RIGHT_CORNER, LEFT_MOUTH_CORNER, RIGHT_MOUTH_CORNER]


@dataclass
class HeadPose:
    yaw: float  # degrees, negative = turned left, positive = turned right
    pitch: float  # degrees, negative = looking down, positive = looking up
    roll: float  # degrees, head tilt


def estimate_head_pose(landmarks: np.ndarray, crop_width: int, crop_height: int) -> HeadPose | None:
    """Estimate yaw/pitch/roll from normalized FaceMesh landmarks.

    Args:
        landmarks: (468 or 478, 3) normalized landmark array from face_mesh.extract()
        crop_width, crop_height: pixel dimensions of the face crop the landmarks were computed on
    """
    if landmarks is None or len(landmarks) <= max(_LANDMARK_INDICES):
        return None

    image_points = np.array(
        [
            (landmarks[i][0] * crop_width, landmarks[i][1] * crop_height)
            for i in _LANDMARK_INDICES
        ],
        dtype=np.float64,
    )

    focal_length = crop_width
    center = (crop_width / 2, crop_height / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype=np.float64
    )
    dist_coeffs = np.zeros((4, 1))  # assume no lens distortion

    success, rotation_vector, _ = cv2.solvePnP(
        _MODEL_POINTS_3D, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    yaw, pitch, roll = _rotation_matrix_to_euler_degrees(rotation_matrix)
    return HeadPose(yaw=yaw, pitch=pitch, roll=roll)


def _rotation_matrix_to_euler_degrees(R: np.ndarray) -> tuple[float, float, float]:
    """Convert a 3x3 rotation matrix to yaw/pitch/roll in degrees."""
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
        roll = np.arctan2(R[2, 1], R[2, 2])
    else:
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0.0
        roll = np.arctan2(-R[1, 2], R[1, 1])

    return float(np.degrees(yaw)), float(np.degrees(pitch)), float(np.degrees(roll))
