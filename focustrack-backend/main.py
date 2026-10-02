"""
FocusTrack Backend -- FastAPI entry point.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
or simply:
    python main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import analytics_routes, image_routes, logs_routes
from services import video_service
from utils.config import ensure_directories
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directories()
    logger.info("FocusTrack backend starting up.")
    yield
    # Flush and close the session video writer cleanly on shutdown instead
    # of leaving a partially-written .mp4 (VideoWriter must be released to
    # finalize the file's container/index).
    video_service.finalize()
    logger.info("FocusTrack backend shut down.")


app = FastAPI(
    title="FocusTrack Backend",
    description="Local-first smart classroom attentiveness monitoring API.",
    version="1.0.0",
    lifespan=lifespan,
)

# The React dashboard runs on a different local port (Vite dev server);
# allow it to call this API from the same machine/LAN during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # single local classroom deployment -- no public exposure
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_routes.router)
app.include_router(analytics_routes.router)
app.include_router(logs_routes.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "focustrack-backend"}


if __name__ == "__main__":
    import uvicorn

    from utils.config import HOST, PORT

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
