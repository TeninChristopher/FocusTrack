"""
Attention scoring.

Combines head pose (yaw/pitch deviation from facing-forward) and eye
openness into a single 0-100 attention score, then buckets it into the
same three status bands the frontend already uses:
  >= 80              -> Highly Attentive
  55-79               -> Partially Attentive
  < 55                -> Distracted

Design: this is a transparent, tunable weighted-penalty model rather than
a trained classifier -- appropriate for a final-year project where the
scoring logic needs to be explainable, not a black box.
"""

from dataclasses import dataclass

from ai.eye_analysis import EyeState
from ai.head_pose import HeadPose
from utils.config import (
    ATTENTION_HIGH_THRESHOLD,
    ATTENTION_PARTIAL_THRESHOLD,
    MAX_ACCEPTABLE_PITCH_DEG,
    MAX_ACCEPTABLE_YAW_DEG,
)
from utils.helpers import clamp

# Weights: eyes-closed dominates (a student with closed eyes isn't attentive
# regardless of head orientation), head pose is the secondary signal.
_EYES_CLOSED_PENALTY = 55
_YAW_WEIGHT = 30
_PITCH_WEIGHT = 15


@dataclass
class AttentionResult:
    score: int  # 0-100
    status: str  # "Highly Attentive" | "Partially Attentive" | "Distracted"
    reason: str  # short human-readable primary cause, used in event logs


def compute_attention(head_pose: HeadPose | None, eye_state: EyeState | None) -> AttentionResult:
    if head_pose is None and eye_state is None:
        # Face detected but mesh/pose failed (e.g. extreme angle) -- treat as fully distracted
        # rather than guessing, since we have no signal to score on.
        return AttentionResult(score=0, status="Distracted", reason="Face angle unreadable")

    score = 100.0
    reasons: list[str] = []

    if eye_state is not None and eye_state.eyes_closed:
        score -= _EYES_CLOSED_PENALTY
        reasons.append("Eyes Closed")

    if head_pose is not None:
        yaw_ratio = clamp(abs(head_pose.yaw) / MAX_ACCEPTABLE_YAW_DEG, 0, 1)
        pitch_ratio = clamp(abs(head_pose.pitch) / MAX_ACCEPTABLE_PITCH_DEG, 0, 1)

        score -= yaw_ratio * _YAW_WEIGHT
        score -= pitch_ratio * _PITCH_WEIGHT

        if yaw_ratio >= 0.7:
            reasons.append("Looking Left" if head_pose.yaw < 0 else "Looking Right")
        elif pitch_ratio >= 0.7:
            reasons.append("Looking Down" if head_pose.pitch < 0 else "Looking Up")

    score = int(clamp(score, 0, 100))

    if score >= ATTENTION_HIGH_THRESHOLD:
        status = "Highly Attentive"
    elif score >= ATTENTION_PARTIAL_THRESHOLD:
        status = "Partially Attentive"
    else:
        status = "Distracted"

    reason = reasons[0] if reasons else "Looking Forward"
    return AttentionResult(score=score, status=status, reason=reason)
