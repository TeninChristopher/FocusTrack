"""
Logs routes -- event logs, session listing, and session video retrieval
for the dashboard's Logs page.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from services import analytics_service, video_service

router = APIRouter(prefix="/api", tags=["logs"])


@router.get("/logs")
def get_logs(date: str | None = Query(default=None, description="YYYY-MM-DD"), limit: int = 100):
    """Attention-drop and eyes-closed events, optionally filtered to one date."""
    return analytics_service.get_logs(date=date, limit=limit)


@router.get("/sessions")
def get_sessions():
    """All recorded sessions (one per day), for the recordings list."""
    return analytics_service.get_sessions()


@router.get("/video/{session_id}")
def get_video(session_id: str):
    """Stream a session's recorded video file."""
    session = analytics_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    video_path = video_service.get_video_path(session_id)
    if video_path is None:
        raise HTTPException(status_code=404, detail=f"Video file for session '{session_id}' not found on disk.")

    return FileResponse(video_path, media_type="video/mp4", filename=video_path.name)
