"""Record Open Duck Mini with the phone head walking, for the promo's ARKit scene.

    cd ../inf-open-duck-mini-v2/sim
    uv run --no-project --with mujoco --with onnxruntime --with numpy --with scipy \
        python ../../openhead/tools/promo/duck_walk.py ../../openhead/build/promo/duck.json

Runs Open Duck's walking policy on the `realhead` model (the desk rig's real head on the duck)
in MuJoCo and writes, per film frame, the world pose of every visual mesh as its STL file sees
it, so Blender can replay the walk without MuJoCo. Run from the duck repo's `sim/` folder.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
import story
from sim_test import Sim

SECONDS = story.DUCK_SECONDS


def commands(t: float) -> np.ndarray:
    """Walk ahead, curve left, walk on; the head looks around (what ARKit maps)."""
    c = np.zeros(7)
    c[0] = 0.0 if t < 0.6 else 0.25
    c[2] = 0.45 if 3.0 < t < 5.5 else 0.0
    c[5] = 0.55 * np.sin(2 * np.pi * 0.18 * t)        # head_yaw
    c[4] = 0.12 * np.sin(2 * np.pi * 0.11 * t + 1.0)  # head_pitch
    return c


def main() -> None:
    out = Path(sys.argv[1])
    s = Sim(model="realhead", imu="trunk", head="none", neck_override=True)
    s.commands = commands
    s.err = []
    m, d = s.m, s.d
    root = ET.parse(Path("xmls/open_duck_mini_v2_realhead.xml")).getroot()
    files = {e.get("name"): e.get("file") for e in root.iter("mesh")}
    geoms = [g for g in range(m.ngeom)
             if m.geom_group[g] == 2 and m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH]
    meshes = []
    offsets = []
    for g in geoms:
        mid = m.geom_dataid[g]
        name = m.mesh(mid).name
        meshes.append({"mesh": name, "file": str((Path("xmls/assets") / files.get(name, name + ".stl")).resolve()),
                       "rgba": [float(v) for v in m.geom_rgba[g]]})
        # MuJoCo moves a mesh to its centre of mass; undo that so the raw STL lines up.
        rm = np.zeros(9)
        mujoco.mju_quat2Mat(rm, m.mesh_quat[mid])
        offsets.append((rm.reshape(3, 3), m.mesh_pos[mid].copy()))
    # The screen stand-in (a thin box on the phone) and the camera sites, for the screen and the effects.
    screen = next(g for g in range(m.ngeom)
                  if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_BOX and abs(m.geom_size[g][0] - 0.0699) < 1e-4)
    geoms.append(screen)
    meshes.append({"mesh": "screen", "file": None, "size": [float(v) for v in m.geom_size[screen]]})
    offsets.append((np.eye(3), np.zeros(3)))
    sites = [m.site(n).id for n in ("phone_cam_rear", "phone_cam_front")]
    meshes += [{"mesh": n, "file": None} for n in ("cam_rear", "cam_front")]
    every = round(1 / (story.FPS * m.opt.timestep))
    frames = []
    base = m.body("base").id
    for k in range(int(SECONDS / m.opt.timestep) + 1):
        if k % s.decimation == 0:
            s.step_policy(k * m.opt.timestep)
        mujoco.mj_step(m, d)
        if k % every:
            continue
        row = []
        for g, (rm, pm) in zip(geoms, offsets, strict=True):
            rg = d.geom_xmat[g].reshape(3, 3)
            r = rg @ rm.T
            p = d.geom_xpos[g] - r @ pm
            q = np.zeros(4)
            mujoco.mju_mat2Quat(q, r.flatten())
            row.append([round(float(v), 5) for v in (*p, *q)])
        for site in sites:
            q = np.zeros(4)
            mujoco.mju_mat2Quat(q, d.site_xmat[site])
            row.append([round(float(v), 5) for v in (*d.site_xpos[site], *q)])
        frames.append(row)
    up = d.xmat[base].reshape(3, 3)[:, 2]
    print(f"{len(frames)} frames, base at {d.xpos[base].round(2)}, upright {up[2]:.2f}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"fps": story.FPS, "meshes": meshes, "frames": frames}))
    print("wrote", out)


if __name__ == "__main__":
    main()
