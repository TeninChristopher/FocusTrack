"""
Persistent-ID face tracker, implementing the core ideas of ByteTrack:

1. A constant-velocity Kalman filter predicts each track's next position.
2. Detections are matched to existing tracks by IOU using the Hungarian
   algorithm (scipy.optimize.linear_sum_assignment) -- not simple nearest-
   neighbor -- so ID swaps under crossing/occlusion are minimized.
3. Two-tier matching: high-confidence detections are matched first; any
   still-unmatched tracks then get a second chance to match against
   low-confidence detections before being marked "lost" -- ByteTrack's key
   insight is that low-confidence detections are often real, partially
   occluded objects, not noise, and shouldn't be thrown away too early.
4. A track that goes unmatched isn't deleted immediately -- it survives
   TRACK_LOST_GRACE_FRAMES missed frames ("lost" state) before retirement,
   so a student who briefly turns away or is occluded keeps their ID
   instead of getting a new one when they reappear.

This is a from-scratch NumPy/SciPy implementation rather than a wrapper
around the upstream `bytetrack` package, which depends on Cython
extensions (`cython_bbox`, `lap`) that are unreliable to build in
constrained environments. Behavior matches the algorithm; the exact
upstream package is not a dependency.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment

from utils.config import (
    TRACK_HIGH_CONF_THRESHOLD,
    TRACK_IOU_MATCH_THRESHOLD,
    TRACK_LOST_GRACE_FRAMES,
)


def _iou(box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    if inter_area == 0:
        return 0.0

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter_area / float(area_a + area_b - inter_area)


class _KalmanBoxTracker:
    """Constant-velocity Kalman filter over an 8-dim state: [cx, cy, w, h, vx, vy, vw, vh]."""

    def __init__(self, bbox: tuple[int, int, int, int]):
        x1, y1, x2, y2 = bbox
        cx, cy, w, h = (x1 + x2) / 2.0, (y1 + y2) / 2.0, x2 - x1, y2 - y1

        self.state = np.array([cx, cy, w, h, 0, 0, 0, 0], dtype=np.float64)

        # Constant-velocity transition matrix.
        self.F = np.eye(8)
        for i in range(4):
            self.F[i, i + 4] = 1.0

        self.H = np.zeros((4, 8))
        for i in range(4):
            self.H[i, i] = 1.0

        self.P = np.eye(8) * 10.0
        self.Q = np.eye(8) * 0.5
        self.R = np.eye(4) * 1.0

    def predict(self) -> tuple[int, int, int, int]:
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self._to_bbox()

    def update(self, bbox: tuple[int, int, int, int]) -> None:
        x1, y1, x2, y2 = bbox
        z = np.array([(x1 + x2) / 2.0, (y1 + y2) / 2.0, x2 - x1, y2 - y1])

        y = z - self.H @ self.state
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.state = self.state + K @ y
        self.P = (np.eye(8) - K @ self.H) @ self.P

    def _to_bbox(self) -> tuple[int, int, int, int]:
        cx, cy, w, h = self.state[:4]
        return (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self._to_bbox()


@dataclass
class Track:
    track_id: int
    kalman: _KalmanBoxTracker
    confidence: float = 0.0
    missed_frames: int = 0
    hits: int = 1
    lost: bool = False
    history: list = field(default_factory=list)  # recent centers, for drawing a tracking path

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self.kalman.bbox


class ByteTracker:
    """Stateful multi-object tracker. One instance persists for the whole session
    (owned by tracking_service), fed one frame's detections at a time.
    """

    def __init__(
        self,
        high_conf_threshold: float = TRACK_HIGH_CONF_THRESHOLD,
        iou_threshold: float = TRACK_IOU_MATCH_THRESHOLD,
        lost_grace_frames: int = TRACK_LOST_GRACE_FRAMES,
        max_history: int = 20,
    ):
        self.high_conf_threshold = high_conf_threshold
        self.iou_threshold = iou_threshold
        self.lost_grace_frames = lost_grace_frames
        self.max_history = max_history

        self._tracks: dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: list) -> dict[int, dict]:
        """Advance the tracker by one frame.

        Args:
            detections: list of ai.face_detection.Detection

        Returns:
            {track_id: {"bbox": (x1,y1,x2,y2), "confidence": float, "is_new": bool}}
            for every track currently visible (matched this frame).
        """
        # 1. Predict new positions for all existing tracks.
        for track in self._tracks.values():
            track.kalman.predict()

        high_conf = [d for d in detections if d.confidence >= self.high_conf_threshold]
        low_conf = [d for d in detections if d.confidence < self.high_conf_threshold]

        active_ids = [tid for tid, t in self._tracks.items() if not t.lost]
        matched_ids: set[int] = set()
        results: dict[int, dict] = {}

        # 2. First-pass match: active tracks <-> high-confidence detections.
        remaining_high = self._match_and_update(active_ids, high_conf, matched_ids, results)

        # 3. Second-pass match: tracks still unmatched <-> low-confidence detections.
        #    (ByteTrack's key idea: don't discard low-conf boxes outright -- they often
        #    correspond to a real, partially-occluded student.)
        still_unmatched_ids = [tid for tid in active_ids if tid not in matched_ids]
        self._match_and_update(still_unmatched_ids, low_conf, matched_ids, results)

        # 4. Any high-confidence detections still unmatched become brand-new tracks.
        for det in remaining_high:
            track_id = self._next_id
            self._next_id += 1
            new_track = Track(track_id=track_id, kalman=_KalmanBoxTracker(det.bbox), confidence=det.confidence)
            new_track.history.append(new_track.kalman._to_bbox()[:2])
            self._tracks[track_id] = new_track
            results[track_id] = {"bbox": det.bbox, "confidence": det.confidence, "is_new": True}

        # 5. Age out tracks that weren't matched this frame.
        for tid, track in list(self._tracks.items()):
            if tid not in matched_ids and tid not in results:
                track.missed_frames += 1
                track.lost = track.missed_frames > 0
                if track.missed_frames > self.lost_grace_frames:
                    del self._tracks[tid]  # genuinely gone -- retire the ID

        return results

    def _match_and_update(
        self,
        candidate_ids: list[int],
        candidate_detections: list,
        matched_ids: set[int],
        results: dict[int, dict],
    ) -> list:
        """IOU + Hungarian-match `candidate_ids` tracks against `candidate_detections`.

        Returns the list of detections that remained unmatched.
        """
        if not candidate_ids or not candidate_detections:
            return list(candidate_detections)

        iou_matrix = np.zeros((len(candidate_ids), len(candidate_detections)))
        for i, tid in enumerate(candidate_ids):
            for j, det in enumerate(candidate_detections):
                iou_matrix[i, j] = _iou(self._tracks[tid].bbox, det.bbox)

        # Hungarian algorithm minimizes cost -- use (1 - IOU) so max IOU wins.
        row_idx, col_idx = linear_sum_assignment(1 - iou_matrix)

        matched_det_indices = set()
        for r, c in zip(row_idx, col_idx):
            if iou_matrix[r, c] < self.iou_threshold:
                continue  # not a real match, IOU too low

            tid = candidate_ids[r]
            det = candidate_detections[c]
            track = self._tracks[tid]

            track.kalman.update(det.bbox)
            track.confidence = det.confidence
            track.missed_frames = 0
            track.lost = False
            track.hits += 1
            track.history.append(((det.x1 + det.x2) // 2, (det.y1 + det.y2) // 2))
            track.history = track.history[-self.max_history :]

            matched_ids.add(tid)
            matched_det_indices.add(c)
            results[tid] = {"bbox": det.bbox, "confidence": det.confidence, "is_new": False}

        return [det for j, det in enumerate(candidate_detections) if j not in matched_det_indices]

    def active_track_count(self) -> int:
        return sum(1 for t in self._tracks.values() if not t.lost)
