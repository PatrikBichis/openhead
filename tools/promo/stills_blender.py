"""Still renders of the rig for the desk body's website, from the promo scene.

    blender -b build/promo/scene.blend -P tools/promo/stills_blender.py -- OUT_DIR

Uses the scene scene_blender.py saved (--save): the same set, light and materials, at a quiet
frame, without the person and the effects, from a few fixed viewpoints.
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1])
FRAME = 40                        # intro, before anything else happens
VIEWS = {  # name: (camera position, look at, lens)
    "hero": ((0.62, -0.34, 0.38), (0.05, 0.0, 0.2), 45),
    "front": ((0.75, 0.0, 0.3), (0.05, 0.0, 0.2), 40),
    "side": ((0.06, -0.78, 0.3), (0.05, 0.0, 0.2), 40),
    "back": ((-0.55, 0.42, 0.42), (0.05, 0.0, 0.22), 40),
}

sc = bpy.context.scene


def hidden(o):
    while o:
        if o.name.startswith(("person", "pt", "sound")):
            return True
        o = o.parent
    return False


cam = sc.camera
target = bpy.data.objects["cam target"]
for owner in (cam, target, cam.data):
    owner.animation_data_clear()
sc.frame_set(FRAME + 1)
for o in sc.objects:                # after frame_set, which applies the keyed visibility
    if hidden(o):
        o.animation_data_clear()
        o.hide_render = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1600, 1200, 100
OUT.mkdir(parents=True, exist_ok=True)
for name, (pos, look, lens) in VIEWS.items():
    cam.location = Vector(pos)
    target.location = Vector(look)
    cam.data.lens = lens
    cam.data.dof.aperture_fstop = 5.6
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("wrote", name)
