"""
Centralized configuration for FocusTrack backend.

Single classroom, single ESP32-CAM, local-first deployment -- config stays
flat and simple. All tunable pipeline behavior (thresholds, grace periods,
frame sizes) lives here so nothing is a magic number buried in a service.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Storage paths -----------------------------------------------------
RAW_DIR = BASE_DIR / "uploads" / "raw"
PROCESSED_DIR = BASE_DIR / "uploads" / "processed"
VIDEOS_DIR = BASE_DIR / "videos"
DATA_DIR = BASE_DIR / "data"

CURRENT_STATUS_FILE = DATA_DIR / "current_status.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
LOGS_FILE = DATA_DIR / "logs.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"

# --- Server --------------------------------------------------------------
HOST = os.getenv("FOCUSTRACK_HOST", "0.0.0.0")
PORT = int(os.getenv("FOCUSTRACK_PORT", "8000"))

# --- Frame processing ----------------------------------------------------
# Downscale before running inference to keep CPU latency predictable at
# ~5fps; annotated output is scaled back up to the original resolution.
MAX_FRAME_DIMENSION = int(os.getenv("FOCUSTRACK_MAX_FRAME_DIM", "640"))

# --- Face detection / mesh ------------------------------------------------
FACE_DETECTION_CONFIDENCE = float(os.getenv("FOCUSTRACK_FACE_DET_CONF", "0.5"))
FACE_MESH_CONFIDENCE = float(os.getenv("FOCUSTRACK_FACE_MESH_CONF", "0.5"))
MAX_FACES = int(os.getenv("FOCUSTRACK_MAX_FACES", "40"))

# --- Tracking (ByteTrack-style) -------------------------------------------
# How many consecutive missed frames a track survives before its ID is
# retired. At ~5fps, 10 frames ~= 2 seconds of grace for brief occlusion.
TRACK_LOST_GRACE_FRAMES = int(os.getenv("FOCUSTRACK_TRACK_GRACE_FRAMES", "10"))
TRACK_HIGH_CONF_THRESHOLD = float(os.getenv("FOCUSTRACK_TRACK_HIGH_CONF", "0.6"))
TRACK_IOU_MATCH_THRESHOLD = float(os.getenv("FOCUSTRACK_TRACK_IOU_THRESHOLD", "0.3"))

# --- Attention scoring -----------------------------------------------------
# Score bands mirror the frontend's attentionStatus() thresholds exactly.
ATTENTION_HIGH_THRESHOLD = 80
ATTENTION_PARTIAL_THRESHOLD = 55

# Eye Aspect Ratio below this is considered "closed".
EAR_CLOSED_THRESHOLD = float(os.getenv("FOCUSTRACK_EAR_THRESHOLD", "0.20"))

# Yaw/pitch (degrees) beyond which a head is considered "turned away".
MAX_ACCEPTABLE_YAW_DEG = 35.0
MAX_ACCEPTABLE_PITCH_DEG = 25.0

# --- Event logging ---------------------------------------------------------
# Only log an "eyes closed" event once it persists this long, to avoid
# flooding logs.json with blink-length noise.
EYES_CLOSED_MIN_DURATION_SEC = float(os.getenv("FOCUSTRACK_EYES_CLOSED_MIN_SEC", "3.0"))
# Only log an attention-drop event on threshold *crossing*, not every frame.
ATTENTION_DROP_LOG_THRESHOLD = 50

# --- Device / system status --------------------------------------------------
DEVICE_OFFLINE_THRESHOLD_SEC = int(os.getenv("FOCUSTRACK_DEVICE_OFFLINE_SEC", "10"))

# --- Video ----------------------------------------------------------------
VIDEO_FPS = float(os.getenv("FOCUSTRACK_VIDEO_FPS", "5.0"))
VIDEO_CODEC = os.getenv("FOCUSTRACK_VIDEO_CODEC", "mp4v")


def ensure_directories() -> None:
    """Create all storage directories on startup if they don't already exist."""
    for path in (RAW_DIR, PROCESSED_DIR, VIDEOS_DIR, DATA_DIR):
        path.mkdir(parents=True, exist_ok=True)
