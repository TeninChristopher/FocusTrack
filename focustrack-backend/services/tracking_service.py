"""
Tracking service.

Owns the one ByteTracker instance for the whole session -- tracking state
(Kalman filters, track IDs, history) must persist across frames, so this
is a module-level singleton rather than something re-created per request.
"""

from ai.byte_tracker import ByteTracker
from ai.face_detection import Detection

_tracker = ByteTracker()


def update_tracks(detections: list[Detection]) -> dict[int, dict]:
    """Advance tracking by one frame. See ByteTracker.update for return shape."""
    return _tracker.update(detections)


def get_track_history(track_id: int) -> list[tuple[int, int]]:
    track = _tracker._tracks.get(track_id)
    return list(track.history) if track else []


def active_track_count() -> int:
    return _tracker.active_track_count()


def reset() -> None:
    """Reset all tracking state -- e.g. when starting a new session/day."""
    global _tracker
    _tracker = ByteTracker()
