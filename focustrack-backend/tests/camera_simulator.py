"""
Camera simulator.

Simulates the ESP32-CAM using the laptop's webcam so the full backend
pipeline can be tested end-to-end before hardware is available. Captures
a frame every 0.2s and POSTs it to /upload-image -- the exact same route
and multipart contract the real ESP32-CAM will use, so this script is a
faithful stand-in, not a separate test path.

Usage:
    python tests/camera_simulator.py
    python tests/camera_simulator.py --url http://localhost:8000/upload-image --camera 0
"""

import argparse
import time

import cv2
import requests

CAPTURE_INTERVAL_SEC = 0.2


def run(upload_url: str, camera_index: int) -> None:
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open webcam at index {camera_index}.")

    print(f"Camera simulator started. Streaming to {upload_url} every {CAPTURE_INTERVAL_SEC}s.")
    print("Press Ctrl+C to stop.")

    frame_count = 0
    try:
        while True:
            loop_start = time.monotonic()

            ok, frame = capture.read()
            if not ok:
                print("Warning: failed to read frame from webcam, retrying...")
                time.sleep(CAPTURE_INTERVAL_SEC)
                continue

            ok, encoded = cv2.imencode(".jpg", frame)
            if not ok:
                print("Warning: failed to JPEG-encode frame, skipping.")
                continue

            try:
                response = requests.post(
                    upload_url,
                    files={"file": ("frame.jpg", encoded.tobytes(), "image/jpeg")},
                    timeout=5,
                )
                frame_count += 1
                if response.ok:
                    body = response.json()
                    print(
                        f"[frame {frame_count}] OK -- "
                        f"{body.get('students_detected', '?')} student(s) detected"
                    )
                else:
                    print(f"[frame {frame_count}] Server error {response.status_code}: {response.text}")
            except requests.RequestException as exc:
                print(f"[frame {frame_count}] Upload failed: {exc}")

            # Maintain a steady 0.2s cadence regardless of how long processing took.
            elapsed = time.monotonic() - loop_start
            time.sleep(max(0.0, CAPTURE_INTERVAL_SEC - elapsed))

    except KeyboardInterrupt:
        print("\nCamera simulator stopped.")
    finally:
        capture.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate the ESP32-CAM using a laptop webcam.")
    parser.add_argument(
        "--url", default="http://localhost:8000/upload-image", help="Backend upload endpoint URL."
    )
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default 0).")
    args = parser.parse_args()

    run(args.url, args.camera)
