"""
Analysis service.

The orchestrator: given one uploaded frame, runs the full pipeline
(detect -> track -> mesh -> pose -> eyes -> score -> annotate -> persist)
and drives every other service/ai module. This is the only place that
knows the *order* of the pipeline; each step itself lives in its own
focused module.

FaceDetector and FaceMeshExtractor are constructed once at module load
(expensive MediaPipe graph construction) and reused across every frame.
"""

from pathlib import Path

from ai.attention_score import compute_attention
from ai.eye_analysis import analyze_eyes
from ai.face_detection import Detection, FaceDetector
from ai.face_mesh import FaceMeshExtractor
from ai.head_pose import estimate_head_pose
from services import analytics_service, image_service, tracking_service, video_service
from utils.helpers import now_iso
from utils.logger import get_logger

logger = get_logger(__name__)

_face_detector = FaceDetector()
_face_mesh = FaceMeshExtractor()


def process_frame(raw_path: Path) -> dict:
    """Run the full AI pipeline on one uploaded frame.

    Returns a summary dict describing what was processed, for the route's
    response body. Raises on unrecoverable failure (caller decides whether
    to keep or discard the raw file based on whether this raises).
    """
    frame = image_service.load_image(raw_path)
    if frame is None:
        raise ValueError(f"Could not decode image at {raw_path}")

    original_h, original_w = frame.shape[:2]
    inference_frame, scale_to_original = image_service.resize_for_inference(frame)

    # Step 1: face detection (on the downscaled frame, for predictable CPU latency).
    detections = _face_detector.detect(inference_frame)

    # Scale detection boxes back up to original-frame coordinates before tracking/annotation,
    # so IDs and drawn boxes are stable regardless of the inference resize factor.
    for det in detections:
        det.x1 = int(det.x1 * scale_to_original)
        det.y1 = int(det.y1 * scale_to_original)
        det.x2 = int(det.x2 * scale_to_original)
        det.y2 = int(det.y2 * scale_to_original)

    # Step 2: tracking -- assign/maintain persistent IDs.
    tracked = tracking_service.update_tracks(detections)

    # Steps 3-5: per-face mesh -> head pose + eye analysis -> attention score.
    tracked_faces = []
    for track_id, info in tracked.items():
        x1, y1, x2, y2 = info["bbox"]
        crop_w, crop_h = max(1, x2 - x1), max(1, y2 - y1)

        # Reconstruct a Detection-like object for the mesh extractor's crop logic.
        det = Detection(x1, y1, x2, y2, info["confidence"])
        landmarks = _face_mesh.extract(frame, det)

        head_pose = estimate_head_pose(landmarks, crop_w, crop_h) if landmarks is not None else None
        eye_state = analyze_eyes(landmarks) if landmarks is not None else None

        attention = compute_attention(head_pose, eye_state)

        tracked_faces.append(
            {
                "track_id": track_id,
                "bbox": (x1, y1, x2, y2),
                "confidence": info["confidence"],
                "attention_score": attention.score,
                "attention_status": attention.status,
                "reason": attention.reason,
                "history": tracking_service.get_track_history(track_id),
            }
        )

    # Annotate + persist processed image.
    annotated = image_service.annotate_frame(frame, tracked_faces)
    processed_filename = raw_path.stem.replace("raw_", "") + "_processed.jpg"
    image_service.save_processed_image(annotated, processed_filename)

    # Append to the running session video.
    session_id, video_filename = video_service.append_frame(annotated)
    analytics_service.register_session_frame(session_id, video_filename)

    # Update all JSON state.
    upload_time = now_iso()
    analytics_service.update_current_status(tracked_faces, device_last_seen=upload_time)
    analytics_service.update_analytics(tracked_faces)
    analytics_service.evaluate_and_log_events(tracked_faces)

    return {
        "processed_filename": processed_filename,
        "students_detected": len(tracked_faces),
        "session_id": session_id,
        "frame_size": {"width": original_w, "height": original_h},
    }
