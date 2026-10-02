"""
Image ingestion route.

POST /upload-image is the single entry point both the real ESP32-CAM and
tests/camera_simulator.py send frames to -- identical contract for both,
so the simulator is a faithful stand-in before hardware is available.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile

from services import analysis_service, image_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["image"])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Receive one frame, run it through the full AI pipeline, and return a summary.

    The raw file is deleted automatically once processing succeeds -- only
    the annotated result in uploads/processed/ is kept.
    """
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type '{file.content_type}'.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    raw_filename = f"raw_{timestamp}_{uuid.uuid4().hex[:6]}.jpg"
    raw_path = image_service.save_raw_image(image_bytes, raw_filename)

    try:
        result = analysis_service.process_frame(raw_path)
    except Exception as exc:
        # Deliberately do NOT delete the raw file on failure -- keep it for debugging
        # instead of silently losing a frame that failed mid-pipeline.
        logger.exception("Frame processing failed for %s", raw_path)
        raise HTTPException(status_code=500, detail=f"Frame processing failed: {exc}") from exc

    # Only delete the raw upload after confirmed pipeline success.
    image_service.delete_raw_image(raw_path)

    return {"status": "processed", **result}
