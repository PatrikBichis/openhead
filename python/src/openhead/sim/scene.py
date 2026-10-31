"""Synthetic people and pose for the simulator's camera modes (protocol 0.2).

Two people in front of the head: one walks slowly from side to side, the other comes and
goes. The camera view is mirrored, like a selfie, so a person to the head's left (+bearing)
appears on the right of the screen; the page draws them where their `box` is.
"""

from __future__ import annotations

import math

from . import imu

HFOV = 68.0  # front camera, landscape, degrees
VFOV = 40.0


def _face(fid: int, cx: float, cy: float, w: float, confidence: float) -> dict:
    h = w * 2.1  # boxes are in screen units; the screen is about twice as wide as high
    return {
        "id": fid,
        "bearing": round((cx - 0.5) * HFOV, 2),
        "elevation": round((0.5 - cy) * VFOV, 2),
        "size": round(w, 3),
        "confidence": round(confidence, 2),
        "box": {"x": round(cx - w / 2, 4), "y": round(cy - h / 2, 4), "w": round(w, 4), "h": round(h, 4)},
    }


def faces_at(t: float, *, boxes: bool = True) -> list[dict]:
    """People in view at `t` seconds; without `boxes` (ARKit) only the nearest, without a box."""
    out = [_face(1, 0.5 + 0.28 * math.sin(0.4 * t), 0.4 + 0.03 * math.sin(1.3 * t), 0.17, 0.95)]
    if (t % 12) < 8:  # the second person is in view 8 s out of 12
        out.append(_face(2, 0.78 - 0.05 * math.sin(0.25 * t), 0.43, 0.09, 0.82))
    if not boxes:
        nearest = max(out, key=lambda f: f["size"])
        nearest = {k: v for k, v in nearest.items() if k != "box"}
        nearest["distance_m"] = round(0.12 / nearest["size"], 2)
        return [nearest]
    return out


def pose_at(t: float) -> dict:
    """ARKit-like pose: tracking starts limited, then the head drifts on a small circle."""
    q = imu.sample(t)["q"]
    state = "limited" if t < 1.0 else "normal"
    pose = {
        "position": [round(0.25 * math.sin(0.2 * t), 4), round(0.02 * math.sin(0.9 * t), 4),
                     round(0.25 * (math.cos(0.2 * t) - 1), 4)],
        "q": q,
        "tracking_state": state,
        "frame": "world",
        "sensor_time_s": round(t, 4),
    }
    if state == "limited":
        pose["tracking_reason"] = "initializing"
    return pose
