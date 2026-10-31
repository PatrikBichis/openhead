"""Synthetic IMU: a head slowly looking around, in the protocol's device frame.

Device frame: +x right, +y up, +z out of the screen (portrait). Reference frame: the
device standing upright. `accel` is specific force (+9.81 on +y at rest upright).
"""

from __future__ import annotations

import math

G = 9.81

Quat = tuple[float, float, float, float]  # x, y, z, w


def _axis_angle(axis: tuple[float, float, float], angle: float) -> Quat:
    s = math.sin(angle / 2)
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(angle / 2))


def _mul(a: Quat, b: Quat) -> Quat:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _rotate(q: Quat, v: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z, _w = _mul(_mul(q, (*v, 0.0)), (-q[0], -q[1], -q[2], q[3]))
    return (x, y, z)


def sample(t: float) -> dict:
    """IMU payload at time `t` seconds."""
    yaw, d_yaw = 0.35 * math.sin(0.5 * t), 0.35 * 0.5 * math.cos(0.5 * t)
    pitch, d_pitch = 0.12 * math.sin(0.31 * t + 1), 0.12 * 0.31 * math.cos(0.31 * t + 1)
    roll, d_roll = 0.04 * math.sin(0.73 * t), 0.04 * 0.73 * math.cos(0.73 * t)
    q = _mul(_mul(_axis_angle((0, 1, 0), yaw), _axis_angle((1, 0, 0), pitch)),
             _axis_angle((0, 0, 1), roll))
    # Specific force seen by the device: the upward reaction to gravity, rotated into its frame.
    accel = _rotate((-q[0], -q[1], -q[2], q[3]), (0.0, G, 0.0))
    return {
        "q": [round(c, 6) for c in q],
        "gyro": [round(d_pitch, 6), round(d_yaw, 6), round(d_roll, 6)],
        "accel": [round(c, 5) for c in accel],
        "frame": "device",
        "sensor_time_s": round(t, 4),
    }
