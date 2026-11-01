"""The promo film's timeline: one source of truth for the 3D scene, the screen and the labels.

Everything is a pure function of the frame number, so the Blender render, the face engine
frames (screen.py) and the overlay (compose.py) stay in step. Rig coordinates are the bench
head's (x forward, y left, z up, metres, desk at z = 0).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

FPS = 30
SIZE = (1920, 1080)

# Site palette (docs/site.css)
CREAM = "#f6e6cc"
CREAM_2 = "#fbf3e6"
INK = "#1d1b22"
INK_2 = "#4a4652"
NAVY = "#1f3a5f"
NAVY_2 = "#16294a"
CORAL = "#e76f51"
TEAL = "#2a9d8f"
GOLD = "#ffc857"


@dataclass(frozen=True)
class Scene:
    key: str
    start: float
    end: float
    title: str
    text: str
    sensors: tuple[str, ...] = ()
    screen: str = "face"      # face | camera
    emotion: str = "neutral"
    subtitle: str = ""


SCENES = [
    Scene("intro", 0, 5, "OpenHead", "An iPhone becomes a robot head. Here: a desk AI assistant.",
          (), emotion="happy"),
    Scene("follow", 5, 12.5, "Face tracking", "The front camera finds you; the neck and the eyes follow.",
          ("front",), emotion="curious"),
    Scene("talk", 12.5, 18.5, "Talks and shows text", "Subtitles with a moving mouth; sound goes to the speaker.",
          ("front", "speaker"), emotion="happy", subtitle="Your 10:00 meeting starts in five minutes."),
    Scene("sensing", 18.5, 26, "Front and back camera at once",
          "ARKit: world tracking with the back camera, your face with the front.",
          ("front", "back", "imu"), emotion="focused"),
    Scene("camera", 26, 31, "Camera view with HUD", "What the head sees, with faces, compass and horizon.",
          ("front", "imu", "compass"), screen="camera", emotion="neutral"),
    Scene("sensors", 31, 37, "Every sensor, streamed to your agent",
          "IMU, compass, barometer and GPS over Wi-Fi, to Python or any MCP agent.",
          ("imu", "compass", "barometer", "gps", "wifi"), emotion="excited"),
    Scene("end", 37, 41, "OpenHead", "Free on the App Store · open source on GitHub", (), emotion="happy"),
]
LENGTH = SCENES[-1].end
FRAMES = int(LENGTH * FPS)

SENSORS = [  # (key, label, colour)
    ("front", "Front TrueDepth camera", TEAL),
    ("back", "Back camera + ARKit SLAM", GOLD),
    ("imu", "Accelerometer + gyroscope", CORAL),
    ("compass", "Magnetometer / compass", CORAL),
    ("barometer", "Barometer", CORAL),
    ("gps", "GPS / GNSS", CORAL),
    ("speaker", "Speaker (Bluetooth)", NAVY),
    ("wifi", "Wi-Fi link to the agent", NAVY),
]

HEAD = (0.075, 0.0, 0.29)        # roughly the phone's centre with the neck at rest
CAMERA_POS = (1.4, -0.9, 0.6)    # default viewpoint, for gaze "at the viewer"
LAPTOP = (0.15, 0.42, 0.0)


def scene_at(t: float) -> Scene:
    for s in SCENES:
        if t < s.end:
            return s
    return SCENES[-1]


def smooth(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mix(a: float, b: float, k: float) -> float:
    return a + (b - a) * k


def person(t: float) -> tuple[float, float, float]:
    """Head of the person at the desk: drifts in front of the rig during face tracking."""
    base = (0.62, 0.05, 0.43)
    if t < 5:
        return base
    u = t - 5
    y = 0.05 + 0.28 * math.sin(u * 0.75) * (1 if t < 31 else max(0.0, 1 - (t - 31) / 2))
    z = 0.43 + 0.04 * math.sin(u * 1.3 + 0.4)
    x = 0.62 - 0.06 * math.sin(u * 0.4)
    return (x, y, z)


def _aim(target: tuple[float, float, float]) -> tuple[float, float]:
    dx, dy, dz = (target[0] - HEAD[0], target[1] - HEAD[1], target[2] - HEAD[2])
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(dz, math.hypot(dx, dy))
    return yaw, pitch


def look_target(t: float) -> tuple[float, float, float]:
    """Where the head wants to look."""
    s = scene_at(t)
    if s.key in ("follow", "talk", "camera"):
        return person(t)
    if s.key == "sensing":
        u = (t - s.start) / (s.end - s.start)
        ang = math.sin(u * math.pi * 2) * 1.0  # sweep the room: ±57°
        return (HEAD[0] + math.cos(ang), HEAD[1] + math.sin(ang), HEAD[2] + 0.1 * math.sin(u * 9))
    if s.key == "sensors":
        return (LAPTOP[0], LAPTOP[1], 0.18)
    return CAMERA_POS


def _target_angles(t: float) -> tuple[float, float]:
    # Blend between scene targets over 0.6 s so cuts in intent stay smooth.
    yaw, pitch = _aim(look_target(t))
    s = scene_at(t)
    k = smooth((t - s.start) / 0.6)
    if k < 1 and s.start > 0:
        py, pp = _aim(look_target(s.start - 1e-3))
        yaw, pitch = mix(py, yaw, k), mix(pp, pitch, k)
    return yaw, pitch


@dataclass
class Frame:
    t: float
    scene: Scene
    joints: dict[str, float] = field(default_factory=dict)
    gaze: tuple[float, float] = (0.0, 0.0)
    person: tuple[float, float, float] = (0.0, 0.0, 0.0)


def _head_angles(t: float) -> tuple[float, float]:
    """The neck lags the target (a first-order filter over the past 0.6 s)."""
    tau = 0.22
    yaw = pitch = 0.0
    wsum = 0.0
    step = 1 / FPS
    k = 0
    while k * step < 0.9:
        w = math.exp(-k * step / tau)
        y, p = _target_angles(max(0.0, t - k * step))
        yaw += w * y
        pitch += w * p
        wsum += w
        k += 1
    return yaw / wsum, pitch / wsum


def frame(n: int) -> Frame:
    t = n / FPS
    s = scene_at(t)
    yaw, pitch = _head_angles(t)
    yaw = max(-1.3, min(1.3, yaw))
    roll = 0.0
    if s.key == "sensors":
        roll = 0.18 * math.sin((t - s.start) * 2.2)
    if s.key == "talk":  # small nods while speaking
        pitch += 0.05 * math.sin((t - s.start) * 5.0)
    # Split the head's pitch between the neck and the head (the neck leans a little forward).
    neck = 0.12 + 0.35 * pitch
    head = 0.65 * pitch
    # Eyes: where the target is, relative to where the head points (they lead the neck).
    ty, tp = _target_angles(t)
    # +x is the viewer's right, which is the head's left (+yaw), as in the engine.
    gaze = (max(-1, min(1, (ty - yaw) / math.radians(30))),
            max(-1, min(1, (tp - pitch) / math.radians(15))))
    if s.key in ("intro", "end"):
        gaze = (0.0, 0.0)
    return Frame(t, s, {"neck_pitch": neck, "head_pitch": head, "head_yaw": yaw, "head_roll": roll},
                 gaze, person(t))


def face_bearing(f: Frame) -> tuple[float, float]:
    """Where the person appears to the head's front camera, in degrees (faces topic)."""
    py, pp = _aim(f.person)
    return math.degrees(py - f.joints["head_yaw"]), math.degrees(pp - f.joints["head_pitch"] / 0.65)
