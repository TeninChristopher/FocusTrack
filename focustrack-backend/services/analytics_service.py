"""
Analytics service.

Owns all four JSON data files. After every processed frame,
analysis_service calls `update_all(...)` here with the frame's results,
and this module is the only place that reads/writes:
  data/current_status.json  - live snapshot (who's in frame right now)
  data/analytics.json       - rolling aggregates + trend buckets
  data/logs.json            - attention-drop / eyes-closed events
  data/sessions.json        - session/video metadata

Keeping all JSON mutation behind one module (rather than letting routes or
other services write directly) means the atomic-write guarantee in
utils.helpers is applied consistently everywhere.
"""

from datetime import datetime, timezone

from utils.config import (
    ANALYTICS_FILE,
    ATTENTION_DROP_LOG_THRESHOLD,
    CURRENT_STATUS_FILE,
    DEVICE_OFFLINE_THRESHOLD_SEC,
    EYES_CLOSED_MIN_DURATION_SEC,
    LOGS_FILE,
    SESSIONS_FILE,
)
from utils.helpers import atomic_write_json, new_id, now_iso, read_json
from utils.logger import get_logger

logger = get_logger(__name__)

# In-memory only: tracks per-student state needed to detect threshold
# *crossings* (for de-duplicated event logging) and eyes-closed duration.
# Rebuilt fresh on server restart -- acceptable since it only affects
# event de-dup heuristics, not the persisted JSON data itself.
_student_state: dict[int, dict] = {}


# ---------------------------------------------------------------------------
# current_status.json
# ---------------------------------------------------------------------------

def update_current_status(tracked_faces: list[dict], device_last_seen: str) -> None:
    """Overwrite current_status.json with this frame's live snapshot."""
    students = [
        {
            "id": f"ID{face['track_id']:02d}",
            "track_id": face["track_id"],
            "attention_score": face["attention_score"],
            "attention_status": face["attention_status"],
            "posture": face["reason"],
            "bbox": face["bbox"],
        }
        for face in tracked_faces
    ]

    avg_attention = round(sum(s["attention_score"] for s in students) / len(students)) if students else 0
    distracted = sum(1 for s in students if s["attention_status"] == "Distracted")

    payload = {
        "updated_at": now_iso(),
        "students": students,
        "stats": {
            "studentsDetected": len(students),
            "averageAttention": avg_attention,
            "distractedStudents": distracted,
            "systemStatus": "Online",
        },
        "device": {
            "esp32cam": "Online",
            "backend": "Running",
            "firebase": "Not Configured",  # no cloud services in this deployment
            "lastUpload": device_last_seen,
        },
    }
    atomic_write_json(CURRENT_STATUS_FILE, payload)


# ---------------------------------------------------------------------------
# analytics.json
# ---------------------------------------------------------------------------

def update_analytics(tracked_faces: list[dict]) -> None:
    """Roll this frame's average attention into today's hourly buckets and daily trend."""
    data = read_json(ANALYTICS_FILE, default={"daily_trend": [], "hourly_buckets": {}})

    if tracked_faces:
        avg_attention = sum(f["attention_score"] for f in tracked_faces) / len(tracked_faces)
    else:
        avg_attention = None

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    hour_key = now.strftime("%Y-%m-%d %H:00")

    if avg_attention is not None:
        bucket = data["hourly_buckets"].setdefault(hour_key, {"sum": 0.0, "count": 0})
        bucket["sum"] += avg_attention
        bucket["count"] += 1

        daily_entry = next((d for d in data["daily_trend"] if d["date"] == today), None)
        if daily_entry is None:
            daily_entry = {"date": today, "sum": 0.0, "count": 0}
            data["daily_trend"].append(daily_entry)
        daily_entry["sum"] += avg_attention
        daily_entry["count"] += 1

    atomic_write_json(ANALYTICS_FILE, data)


def get_analytics_summary() -> dict:
    """Read analytics.json and shape it into dashboard-friendly averages."""
    data = read_json(ANALYTICS_FILE, default={"daily_trend": [], "hourly_buckets": {}})

    daily_trend = [
        {"date": d["date"], "attention": round(d["sum"] / d["count"]) if d["count"] else 0}
        for d in data.get("daily_trend", [])
    ]

    period_wise = [
        {"period": hour.split(" ")[1], "attention": round(b["sum"] / b["count"]) if b["count"] else 0}
        for hour, b in sorted(data.get("hourly_buckets", {}).items())
    ]

    return {"dailyTrend": daily_trend, "periodWise": period_wise}


# ---------------------------------------------------------------------------
# logs.json
# ---------------------------------------------------------------------------

def evaluate_and_log_events(tracked_faces: list[dict]) -> None:
    """Compare this frame's per-student state to the last frame's and log
    only genuine *events* (threshold crossings, sustained eyes-closed) --
    not every frame's raw score, to keep logs.json from flooding.
    """
    logs = read_json(LOGS_FILE, default=[])
    changed = False
    now = datetime.now(timezone.utc)

    seen_ids = set()
    for face in tracked_faces:
        tid = face["track_id"]
        seen_ids.add(tid)
        prev = _student_state.get(tid, {"last_score": 100, "eyes_closed_since": None})

        # Attention-drop event: only log when crossing *into* the drop zone, not every frame while there.
        if prev["last_score"] >= ATTENTION_DROP_LOG_THRESHOLD and face["attention_score"] < ATTENTION_DROP_LOG_THRESHOLD:
            logs.insert(
                0,
                {
                    "id": new_id("log_"),
                    "time": now.strftime("%H:%M"),
                    "timestamp": now_iso(),
                    "studentId": f"ID{tid:02d}",
                    "type": "Attention Drop",
                    "from": prev["last_score"],
                    "to": face["attention_score"],
                    "reason": face["reason"],
                },
            )
            changed = True

        # Eyes-closed event: log once duration exceeds the minimum, then don't re-log
        # until eyes reopen and close again (eyes_closed_since is cleared on reopen below).
        if face["reason"] == "Eyes Closed":
            if prev["eyes_closed_since"] is None:
                prev["eyes_closed_since"] = now.isoformat()
            else:
                started = datetime.fromisoformat(prev["eyes_closed_since"])
                duration = (now - started).total_seconds()
                if duration >= EYES_CLOSED_MIN_DURATION_SEC and not prev.get("eyes_closed_logged"):
                    logs.insert(
                        0,
                        {
                            "id": new_id("log_"),
                            "time": now.strftime("%H:%M"),
                            "timestamp": now_iso(),
                            "studentId": f"ID{tid:02d}",
                            "type": "Eyes Closed",
                            "duration": f"{int(duration)} sec",
                        },
                    )
                    prev["eyes_closed_logged"] = True
                    changed = True
        else:
            prev["eyes_closed_since"] = None
            prev["eyes_closed_logged"] = False

        prev["last_score"] = face["attention_score"]
        _student_state[tid] = prev

    # Clean up state for students no longer tracked (left frame / track retired).
    for tid in list(_student_state.keys()):
        if tid not in seen_ids:
            del _student_state[tid]

    if changed:
        atomic_write_json(LOGS_FILE, logs[:500])  # cap growth -- keep most recent 500 events


def get_logs(date: str | None = None, limit: int = 100) -> list[dict]:
    logs = read_json(LOGS_FILE, default=[])
    if date:
        logs = [l for l in logs if l.get("timestamp", "").startswith(date)]
    return logs[:limit]


# ---------------------------------------------------------------------------
# sessions.json
# ---------------------------------------------------------------------------

def register_session_frame(session_id: str, video_filename: str) -> None:
    """Ensure today's session has an entry in sessions.json, updating its frame count."""
    sessions = read_json(SESSIONS_FILE, default=[])
    session = next((s for s in sessions if s["id"] == session_id), None)

    if session is None:
        session = {
            "id": session_id,
            "date": session_id.replace("session_", "").replace("_", "-"),
            "video_file": video_filename,
            "frame_count": 0,
            "started_at": now_iso(),
        }
        sessions.insert(0, session)

    session["frame_count"] += 1
    session["updated_at"] = now_iso()
    atomic_write_json(SESSIONS_FILE, sessions)


def get_sessions() -> list[dict]:
    return read_json(SESSIONS_FILE, default=[])


def get_session(session_id: str) -> dict | None:
    sessions = read_json(SESSIONS_FILE, default=[])
    return next((s for s in sessions if s["id"] == session_id), None)


# ---------------------------------------------------------------------------
# Device status
# ---------------------------------------------------------------------------

def get_device_status() -> dict:
    status = read_json(CURRENT_STATUS_FILE, default=None)
    default_device = {"esp32cam": "Offline", "backend": "Running", "firebase": "Not Configured", "lastUpload": None}

    if not status or "device" not in status:
        return default_device

    last_upload = status.get("device", {}).get("lastUpload")
    is_online = False
    if last_upload:
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_upload)).total_seconds()
        is_online = elapsed <= DEVICE_OFFLINE_THRESHOLD_SEC

    device = {**default_device, **status.get("device", {})}
    device["esp32cam"] = "Online" if is_online else "Offline"
    return device


def get_heatmap() -> list[dict]:
    """Seat-grid view derived from current_status.json's live students."""
    status = read_json(CURRENT_STATUS_FILE, default=None)
    if status is None:
        return []
    return [
        {"seat": s["track_id"], "id": s["id"], "attention": s["attention_score"]}
        for s in status.get("students", [])
    ]
