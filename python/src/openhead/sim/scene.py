"""Synthetic people, pose, location, environment and camera for the simulator (protocols 0.2-0.5).

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


def hud_values(t: float, mode: str, clients: int) -> dict:
    """What a phone reports to the HUD: battery, thermal state, heading, tilt, position."""
    # The same slow look-around as the synthetic IMU (yaw, pitch, roll), seen from the front.
    values = {"battery": 87, "charging": False, "thermal": "nominal",
              "heading": heading_at(t),
              "pitch": round(math.degrees(0.12 * math.sin(0.31 * t + 1)), 1),
              "roll": round(math.degrees(0.04 * math.sin(0.73 * t)), 1),
              "mode": mode, "clients": clients}
    if mode == "sensing":
        pose = pose_at(t)
        values.update(zip("xyz", pose["position"]))
        values["tracking"] = pose["tracking_state"]
    gps = gps_at(t)
    values.update(lat=gps["lat"], lon=gps["lon"], alt=gps["alt_m"], gps_acc=gps["h_accuracy_m"],
                  pressure=round(env_at(t)["pressure_kpa"] * 10, 1))
    return values


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


HOME = (59.32747, 18.05443, 14.0)  # a park bench in Stockholm; lat, lon, metres above sea level


def gps_at(t: float) -> dict:
    """A walk on a 20 m circle around HOME, one lap in 5 minutes."""
    w = 2 * math.pi / 300
    north, east = 20 * math.sin(w * t), 20 * (1 - math.cos(w * t))
    lat = HOME[0] + north / 111_320
    lon = HOME[1] + east / (111_320 * math.cos(math.radians(HOME[0])))
    course = math.degrees(math.atan2(math.sin(w * t), math.cos(w * t))) % 360
    return {"lat": round(lat, 7), "lon": round(lon, 7), "alt_m": round(HOME[2] + 0.5 * math.sin(w * t), 1),
            "h_accuracy_m": 4.7, "v_accuracy_m": 3.1, "speed_m_s": round(20 * w, 2),
            "course_deg": round(course, 1), "sensor_time_s": round(t, 3)}


def env_at(t: float) -> dict:
    """Barometer that follows the walk's altitude, Earth's field in Stockholm, compass heading."""
    heading = heading_at(t)
    rel = 0.5 * math.sin(2 * math.pi / 300 * t)
    h = math.radians(heading)
    # About 50 uT, 72 degrees down; horizontal part along the screen as the head turns.
    horizontal, down = 15.5, 47.6
    return {"pressure_kpa": round(101.325 - rel * 0.012, 4), "relative_altitude_m": round(rel, 2),
            "magnetic_field_ut": [round(-horizontal * math.sin(h), 2), round(horizontal * math.cos(h), 2),
                                  round(-down, 2)],
            "heading_deg": heading, "heading_ref": "true", "heading_accuracy_deg": 10.0,
            "sensor_time_s": round(t, 3)}


def heading_at(t: float) -> float:
    return round((90 + math.degrees(0.35 * math.sin(0.5 * t))) % 360, 1)


# --- protocol 0.5: camera frames, and LiDAR for a simulated Pro model -------------------------


def camera_jpeg(t: float, mode: str, faces: list[dict], max_px: int) -> tuple[bytes, int, int]:
    """A small drawing of what the camera would see: the people at their boxes (`capture`,
    front camera, mirrored) or a room whose horizon follows the pose (`sensing`, back camera)."""
    from io import BytesIO

    from PIL import Image, ImageDraw

    w, h = max_px, max(1, round(max_px * 390 / 844))
    img = Image.new("RGB", (w, h), (232, 226, 214))
    d = ImageDraw.Draw(img)
    if mode == "capture":
        d.rectangle((0, round(h * 0.62), w, h), fill=(205, 196, 180))  # desk
        for f in sorted(faces, key=lambda f: f["size"]):  # the nearest in front
            b = f.get("box")
            if not b:
                continue
            cx, cy, fw = (b["x"] + b["w"] / 2) * w, (b["y"] + b["h"] / 2) * h, b["w"] * w
            d.ellipse((cx - fw * 0.9, cy + fw * 0.5, cx + fw * 0.9, cy + fw * 2.4), fill=(31, 58, 95))  # shoulders
            d.ellipse((cx - fw / 2, cy - fw * 0.62, cx + fw / 2, cy + fw * 0.62), fill=(224, 180, 150))
            for ex in (-0.18, 0.18):
                d.ellipse((cx + ex * fw - fw * 0.05, cy - fw * 0.12, cx + ex * fw + fw * 0.05, cy - fw * 0.02),
                          fill=(40, 30, 30))
            d.arc((cx - fw * 0.2, cy + fw * 0.05, cx + fw * 0.2, cy + fw * 0.32), 20, 160, fill=(150, 70, 60),
                  width=max(1, round(fw * 0.04)))
    else:
        yaw = math.radians(heading_at(t) - 90)
        horizon = h * horizon_at(t)
        d.rectangle((0, round(horizon), w, h), fill=(196, 186, 168))  # floor
        for i in range(-3, 5):  # door and shelves move as the head turns
            x = ((i * 0.32 - yaw * 0.9) % 2.56 - 0.4) * w
            d.rectangle((x, horizon - h * 0.38, x + w * 0.1, horizon), fill=(42, 157, 143) if i % 2 else (31, 58, 95))
    out = BytesIO()
    img.save(out, format="JPEG", quality=70)
    return out.getvalue(), w, h


def horizon_at(t: float) -> float:
    """Where the floor meets the far wall in the back camera's view (0 top, 1 bottom)."""
    return 0.55 + 0.15 * math.sin(0.31 * t + 1)


def depth_at(t: float, x: float, y: float) -> float:
    """LiDAR distance in a box-shaped room: the floor below the horizon, a wall 2.4 m away above."""
    horizon = horizon_at(t)
    if y > horizon:
        return round(min(5.0, 1.1 / max(0.05, (y - horizon) * 2.2)), 3)
    return round(2.4 + 0.3 * (x - 0.5) ** 2, 3)


def room_mesh() -> list[dict]:
    """ARKit-like mesh anchors for the same room: the floor and two walls, one quad each."""
    import base64
    import struct

    def quad(aid: str, corners: list[tuple[float, float, float]]) -> dict:
        verts = struct.pack("<12f", *[c for p in corners for c in p])
        faces = struct.pack("<6I", 0, 1, 2, 0, 2, 3)
        return {"id": aid, "position": [0.0, 0.0, 0.0], "q": [0.0, 0.0, 0.0, 1.0],
                "vertices": base64.b64encode(verts).decode(), "faces": base64.b64encode(faces).decode()}

    return [
        quad("floor", [(-1.5, -1.2, 0.5), (1.5, -1.2, 0.5), (1.5, -1.2, -2.4), (-1.5, -1.2, -2.4)]),
        quad("wall-front", [(-1.5, -1.2, -2.4), (1.5, -1.2, -2.4), (1.5, 1.2, -2.4), (-1.5, 1.2, -2.4)]),
        quad("wall-left", [(-1.5, -1.2, 0.5), (-1.5, -1.2, -2.4), (-1.5, 1.2, -2.4), (-1.5, 1.2, 0.5)]),
    ]
