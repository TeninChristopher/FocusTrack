# FocusTrack — Local Deployment

Classroom attentiveness monitoring, running entirely on one local machine.
No Firebase, no cloud — images and analysis results are stored on disk.

## Pipeline (current stage)

```
capture_webcam.py  --->  images/  --->  backend (watcher + analysis)  --->  data/focustrack.db  --->  dashboard
(ESP32-CAM substitute)
```

The ESP32-CAM firmware/wiring is intentionally skipped for now.
`capture_webcam.py` stands in for it: it grabs a frame from your laptop's
webcam every 0.5s and drops a JPEG into `images/`, exactly like the camera
eventually will. When the ESP32-CAM is ready, point it at the same
`images/` folder (over the local network) and stop running this script —
nothing else in the system needs to change.

## 1. Install dependencies

```bash
cd focustrack
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Start the backend (serves the API + dashboard together)

```bash
cd backend
python app.py
```

Open the dashboard at **http://localhost:5000**.

The backend polls `images/` every 0.5s, runs face/eye-based attentiveness
detection on each new frame, and stores results in `data/focustrack.db`
(SQLite — auto-created on first run).

## 3. Start the camera substitute (in a second terminal)

```bash
cd focustrack
python capture_webcam.py
```

Useful flags:

```bash
python capture_webcam.py --interval 0.5 --camera 0     # defaults
python capture_webcam.py --preview                      # show a live window
python capture_webcam.py --max-images 200                # auto-stop
```

Frames start appearing on the **Live Monitoring** tab within ~1 second.

## How attentiveness is scored

`backend/analyzer.py` uses OpenCV's built-in Haar cascades:

1. Detect faces in the frame → "students visible."
2. Within each face box, look for eyes → proxy for "facing the
   camera/board" (attentive) vs. "looking down/away" (distracted).
3. `attentiveness_score = attentive_faces / total_faces * 100`

This is a lightweight, dependency-free heuristic appropriate for a
classroom demo. If you want to upgrade accuracy later (e.g. a proper
head-pose or gaze model), only `analyze_image()` needs to change —
the database, API, and dashboard all consume its output unchanged.

## Project layout

```
focustrack/
  images/              # dropped frames land here (ESP32-CAM or capture_webcam.py)
  data/                # focustrack.db (SQLite, auto-created)
  backend/
    app.py             # Flask API + folder watcher + static hosting
    analyzer.py         # attentiveness detection
    database.py          # SQLite access layer
    config.py            # paths & tunables
  frontend/
    index.html          # dashboard shell (Live / Analytics / Logs / History / System)
    style.css
    app.js
  capture_webcam.py     # ESP32-CAM substitute
  requirements.txt
```

## Dashboard tabs

- **Live Monitoring** — current camera frame, live face/attentiveness counts, session controls.
- **Analytics** — rolling 5-minute average score, engagement mix, attentiveness-over-time chart.
- **Event Logs** — session starts/stops, low-attentiveness alerts, missing-face warnings.
- **History** — past sessions with per-frame breakdown.
- **System Status** — watcher health, image counts, last capture/processing time, errors.

## Notes / next steps

- Sessions auto-start when frames begin arriving and auto-close after 30s
  of inactivity (`SESSION_IDLE_TIMEOUT` in `config.py`) — or control them
  manually from the Live tab.
- All storage is local; deleting `data/focustrack.db` resets history.
- When you're ready to bring the ESP32-CAM online, it just needs to save
  JPEGs into `images/` on this machine (e.g. via a small local HTTP
  upload endpoint or a mounted share) — the backend and dashboard require
  no changes.
