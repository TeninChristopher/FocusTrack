# FocusTrack Backend

Local-first FastAPI backend for the FocusTrack smart classroom attentiveness
monitoring system. One classroom, one ESP32-CAM, no cloud services, no
database -- state lives in flat JSON files under `data/`.

## Verified working

This implementation has been exercised end-to-end in development:
`POST /upload-image` → face detection → tracking → face mesh → head
pose/eye analysis → attention scoring → annotated image → session video →
JSON persistence → all `/api/*` read routes. Track IDs persist correctly
across frames for the same face.

## Setup

```bash
cd focustrack-backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` pins `mediapipe==0.10.13` deliberately -- this is the
last version with the legacy `solutions` API, which bundles its face
detection/mesh models inside the pip package itself. Newer mediapipe
versions moved to a Tasks API that requires downloading `.task` model
files separately at runtime; pinning avoids that extra network dependency
for a local classroom deployment.

## Run

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API docs: `http://localhost:8000/docs`

## Test without ESP32-CAM hardware

```bash
python tests/camera_simulator.py
```

Streams your laptop webcam to `/upload-image` every 0.2s, identical to
how the real ESP32-CAM will behave. Use `--url` / `--camera` to point at
a different backend host or webcam index.

## API

| Route | Purpose |
|---|---|
| `POST /upload-image` | Ingest one frame (ESP32-CAM or simulator) |
| `GET /api/status` | Full live snapshot: students, stats, device |
| `GET /api/students` | Just the live student list |
| `GET /api/analytics` | Daily trend + period-wise attention |
| `GET /api/heatmap` | Seat-grid attention view |
| `GET /api/device-status` | ESP32-CAM / backend health |
| `GET /api/logs?date=YYYY-MM-DD` | Attention-drop / eyes-closed events |
| `GET /api/sessions` | Recorded sessions (one per day) |
| `GET /api/video/{session_id}` | Stream a session's recorded video |
| `GET /health` | Liveness check |

## Configuration

All tunables (frame size, detection/tracking thresholds, EAR threshold,
grace periods, video fps/codec) live in `utils/config.py` and are
overridable via `.env` -- see the committed `.env` for defaults and
`utils/config.py` for what each one controls.

## Project structure

```
main.py                 FastAPI app, CORS, router registration, lifespan
routes/                 HTTP layer -- thin, delegates to services/
services/                Business logic + orchestration + JSON persistence
ai/                      Detection, tracking, mesh, pose, eyes, scoring
uploads/raw/             Temporary -- deleted after successful processing
uploads/processed/       Annotated frames, kept
videos/                  Per-day session videos (session_YYYY_MM_DD.mp4)
data/                    JSON state (current_status, analytics, logs, sessions)
utils/                   Config, atomic JSON helpers, logging
tests/camera_simulator.py  Webcam-based ESP32-CAM stand-in
```

## Known limitations (by design, given project scope)

- Pipeline runs synchronously inside the upload request (fine for one
  camera at ~5fps on CPU; would need a background queue for more cameras
  or higher frame rates).
- In-memory event-log de-dup state (`_student_state` in
  `analytics_service.py`) resets on server restart -- only affects
  duplicate-event suppression, not the persisted JSON files themselves.
- No authentication -- appropriate for a local, single-classroom LAN
  deployment; add auth before exposing this beyond that.
