"""
Analytics routes -- read-only endpoints the React dashboard polls for
live classroom state and aggregate analytics.
"""

from fastapi import APIRouter

from services import analytics_service, tracking_service
from utils.config import CURRENT_STATUS_FILE
from utils.helpers import read_json

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/status")
def get_status():
    """Full live snapshot: students, aggregate stats, device status."""
    status = read_json(CURRENT_STATUS_FILE, default=None)
    if not status or "students" not in status:
        return {
            "updated_at": None,
            "students": [],
            "stats": {"studentsDetected": 0, "averageAttention": 0, "distractedStudents": 0, "systemStatus": "Idle"},
            "device": {"esp32cam": "Offline", "backend": "Running", "firebase": "Not Configured", "lastUpload": None},
        }
    return status


@router.get("/students")
def get_students():
    """Just the live student list (used by the Live Student Panel)."""
    status = read_json(CURRENT_STATUS_FILE, default={"students": []})
    return status.get("students", [])


@router.get("/analytics")
def get_analytics():
    """Daily trend + period-wise (hourly) attention aggregates."""
    return analytics_service.get_analytics_summary()


@router.get("/heatmap")
def get_heatmap():
    """Seat-grid attention view derived from the live snapshot."""
    return analytics_service.get_heatmap()


@router.get("/device-status")
def get_device_status():
    """ESP32-CAM / backend / storage health, for the dashboard's status bar."""
    device = analytics_service.get_device_status()
    device["activeTracks"] = tracking_service.active_track_count()
    return device
