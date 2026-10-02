"""
Video service.

Continuously appends annotated frames to a per-day session video using
cv2.VideoWriter. OpenCV's VideoWriter requires a fixed frame size and
doesn't tolerate being reopened sporadically well, so this module keeps
exactly one open writer at a time (for "today"), lazily created on the
first frame written, and exposes `finalize()` to flush/close it cleanly
(e.g. on server shutdown or a date rollover).
"""

from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from utils.config import VIDEO_CODEC, VIDEO_FPS, VIDEOS_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class _SessionVideoWriter:
    """Wraps a single cv2.VideoWriter for one day's session video."""

    def __init__(self):
        self._writer: cv2.VideoWriter | None = None
        self._session_id: str | None = None
        self._frame_size: tuple[int, int] | None = None

    def _session_id_for(self, dt: datetime) -> str:
        return f"session_{dt.strftime('%Y_%m_%d')}"

    def _video_path_for(self, session_id: str) -> Path:
        return VIDEOS_DIR / f"{session_id}.mp4"

    def append_frame(self, frame: np.ndarray) -> tuple[str, str]:
        """Append one frame to today's session video, rolling over to a new
        file/writer automatically at date change.

        Returns (session_id, video_filename).
        """
        now = datetime.now(timezone.utc)
        session_id = self._session_id_for(now)
        height, width = frame.shape[:2]

        needs_new_writer = (
            self._writer is None
            or self._session_id != session_id
            or self._frame_size != (width, height)
        )

        if needs_new_writer:
            self.finalize()  # close any previous writer (date rollover or resolution change)
            VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
            video_path = self._video_path_for(session_id)
            fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
            self._writer = cv2.VideoWriter(str(video_path), fourcc, VIDEO_FPS, (width, height))
            self._session_id = session_id
            self._frame_size = (width, height)
            logger.info("Opened new session video: %s (%dx%d)", video_path, width, height)

        self._writer.write(frame)
        return session_id, self._video_path_for(session_id).name

    def finalize(self) -> None:
        """Flush and close the current writer, if any."""
        if self._writer is not None:
            self._writer.release()
            logger.info("Finalized session video: %s", self._session_id)
            self._writer = None
            self._session_id = None
            self._frame_size = None


# Module-level singleton -- one writer instance for the process lifetime,
# analogous to tracking_service's singleton ByteTracker.
_session_writer = _SessionVideoWriter()


def append_frame(frame: np.ndarray) -> tuple[str, str]:
    """Append an annotated frame to today's session video. Returns (session_id, video_filename)."""
    return _session_writer.append_frame(frame)


def finalize() -> None:
    """Flush and close the current session video. Call on server shutdown."""
    _session_writer.finalize()


def get_video_path(session_id: str) -> Path | None:
    path = VIDEOS_DIR / f"{session_id}.mp4"
    return path if path.exists() else None
