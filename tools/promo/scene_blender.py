"""Build and render the promo's 3D scene in Blender from the bench head's MuJoCo model.

    blender -b -P tools/promo/scene_blender.py -- --rig ../inf-open-duck-mini-v2/cad/benchhead \
        --screen build/promo/screen --assets build/promo/assets --duck build/promo/duck.json \
        --out build/promo/frames [--frames 0:1665] [--scale 100] [--save scene.blend]

The rig (four STS3215 in Open Duck's neck, the phone holder, the tower) comes from
`out/benchhead.xml` and its STL files; the joints move as story.py says, and the phone's
screen plays the frames screen.py rendered with the real face engine. The walking scene
replays Open Duck Mini with the same head, as duck_walk.py recorded it in MuJoCo.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import story

# ---------------------------------------------------------------- helpers

# Properties move between Blender versions; a missing one or an unknown enum value is skipped.
API_DRIFT = (AttributeError, TypeError, ValueError, RuntimeError)


def hex_rgb(h: str, a: float = 1.0) -> tuple[float, float, float, float]:
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def vec(s: str | None, default=(0.0, 0.0, 0.0)) -> Vector:
    return Vector([float(v) for v in s.split()]) if s else Vector(default)


def frame_no(n: int) -> int:
    return n + 1  # Blender frame for story frame n


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def empty(name: str, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.02
    link(e)
    e.parent = parent
    e.location = loc
    return e


MATS: dict[str, bpy.types.Material] = {}


def principled(name, color, rough=0.5, metal=0.0, coat=0.0, emission=None, strength=0.0,
               alpha=1.0, sss=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hex_rgb(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.004, 0.002, 0.002)
    if emission:
        b.inputs["Emission Color"].default_value = hex_rgb(emission)
        b.inputs["Emission Strength"].default_value = strength
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        set_blended(m)
    MATS[name] = m
    return m


def set_blended(m):
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        if hasattr(m, attr):
            with contextlib.suppress(*API_DRIFT):
                setattr(m, attr, val)
    if hasattr(m, "use_transparency_overlap"):
        m.use_transparency_overlap = False


def glow(name, color, strength=4.0, alpha=1.0):
    """Unlit emissive material, optionally see-through (sensor effects)."""
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hex_rgb(color)
    em.inputs["Strength"].default_value = strength
    if alpha < 1:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs["Fac"].default_value = alpha
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        set_blended(m)
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    MATS[name] = m
    return m


def pla(name, color):
    """Printed PLA: satin, with faint layer lines along z."""
    if name in MATS:
        return MATS[name]
    m = principled(name, color, rough=0.42, sss=0.04)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 1250.0  # ~0.2 mm layers in object metres... scaled below
    wave.inputs["Distortion"].default_value = 0.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def key_visible(obj, frames_on: list[tuple[int, int]], total: int):
    """hide_render/hide_viewport keyed so obj shows only in the given story frame ranges."""
    def on(n):
        return any(a <= n < b for a, b in frames_on)
    prev = None
    for n in range(total + 1):
        v = on(n)
        if v != prev:
            obj.hide_render = not v
            obj.hide_viewport = not v
            obj.keyframe_insert("hide_render", frame=frame_no(n))
            obj.keyframe_insert("hide_viewport", frame=frame_no(n))
            prev = v


def scene_range(*keys) -> list[tuple[int, int]]:
    return [(int(s.start * story.FPS), int(s.end * story.FPS)) for s in story.SCENES if s.key in keys]


def constant_interp(obj):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad.action):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def _fcurves(action):
    if hasattr(action, "fcurves") and len(getattr(action, "fcurves", [])):
        return action.fcurves
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out.extend(bag.fcurves)
    return out


# ---------------------------------------------------------------- rig


PRINTED = ("bas", "torn", "telefonhuvud", "bakbage", "neck_left_sheet", "neck_right_sheet",
           "head_pitch_to_yaw", "head_yaw_to_roll")
RED = "#c8121c"


def material_for(mesh: str):
    if any(p in mesh for p in PRINTED):
        return pla("PLA red", RED)
    if "palonier" in mesh:
        return principled("Aluminium", (0.80, 0.80, 0.82, 1), rough=0.28, metal=1.0)
    if "case" in mesh:
        return principled("Servo", "#141416", rough=0.55)
    if "iphone" in mesh:
        return principled("iPhone", "#0c0d10", rough=0.22, metal=0.6, coat=0.6)
    if "lager" in mesh:
        return principled("Steel", (0.62, 0.62, 0.64, 1), rough=0.22, metal=1.0)
    if "uno" in mesh:
        return principled("PCB blue", "#0f3f8c", rough=0.35, coat=0.4)
    if "servoadapter" in mesh:
        return principled("PCB dark", "#1d2b22", rough=0.35, coat=0.4)
    if "bno" in mesh:
        return principled("PCB purple", "#3a2a6e", rough=0.35, coat=0.4)
    if "jabra" in mesh:
        return principled("Fabric", "#1b1c20", rough=0.92)
    return principled("Grey", "#777777")


MESH_CACHE: dict[str, bpy.types.Mesh] = {}


def import_stl(path: Path, scale: float):
    key = str(path)
    if key not in MESH_CACHE:
        bpy.ops.wm.stl_import(filepath=key)
        obj = bpy.context.selected_objects[0]
        MESH_CACHE[key] = obj.data
        bpy.data.objects.remove(obj)
        # the importer's own scale option is not applied to the data; scale the vertices
        MESH_CACHE[key].transform(Matrix.Scale(scale, 4))
    return MESH_CACHE[key]


def build_rig(rig_dir: Path):
    xml = ET.parse(rig_dir / "out" / "benchhead.xml").getroot()
    meshes = {}
    for m in xml.iter("mesh"):
        f = m.get("file").replace("/mnt/c/", "C:/")
        meshes[m.get("name")] = (Path(f), float(m.get("scale", "1").split()[0]))
    joints = {}
    sites = {}
    root = empty("rig")

    def add_geoms(node, parent):
        for g in node.findall("geom"):
            if g.get("type") != "mesh":
                continue  # MuJoCo stand-ins (screen box, painted eyes, floor)
            name = g.get("mesh")
            path, scale = meshes[name]
            data = import_stl(path, scale)
            obj = link(bpy.data.objects.new(name, data))
            obj.parent = parent
            obj.location = vec(g.get("pos"))
            assign(obj, material_for(name))
            smooth_auto(obj)
        for s in node.findall("site"):
            sites[s.get("name")] = (parent, vec(s.get("pos")))

    def walk(node, parent):
        for b in node.findall("body"):
            body = empty(b.get("name"), parent, vec(b.get("pos")))
            j = b.find("joint")
            pivot = body
            if j is not None:
                pivot = empty(j.get("name") + "_joint", body)
                pivot.rotation_mode = "QUATERNION"
                joints[j.get("name")] = (pivot, vec(j.get("axis")))
            add_geoms(b, pivot)
            walk(b, pivot)

    wb = xml.find("worldbody")
    add_geoms(wb, root)
    walk(wb, root)
    return joints, sites


def smooth_auto(obj):
    # Smooth shading split at sharp edges: CAD meshes look clean without faceting.
    with contextlib.suppress(*API_DRIFT):
        obj.data.set_sharp_from_angle(angle=math.radians(35))
        for p in obj.data.polygons:
            p.use_smooth = True


# ---------------------------------------------------------------- set


def build_set(assets: Path):
    # Cyclorama: floor curving up into the wall, cream like the site.
    mesh = bpy.data.meshes.new("cyc")
    verts, faces = [], []
    prof = []
    for i in range(9):  # floor from x=3 to x=-1.2
        prof.append((3.0 - i * 0.525, -0.76))
    r = 0.8
    for i in range(1, 13):
        a = i / 12 * math.pi / 2
        prof.append((-1.2 - math.sin(a) * r, -0.76 + (1 - math.cos(a)) * r))
    prof.append((-2.0, 3.0))
    ys = (-4.0, 4.0)
    for x, z in prof:
        for y in ys:
            verts.append((x, y, z))
    for i in range(len(prof) - 1):
        a, b = i * 2, (i + 1) * 2
        faces.append((a, b, b + 1, a + 1))  # normals face the set
    mesh.from_pydata(verts, [], faces)
    for p in mesh.polygons:
        p.use_smooth = True
    cyc = link(bpy.data.objects.new("cyclorama", mesh))
    # A little self-light keeps the curve even (a studio backdrop is lit on its own).
    assign(cyc, principled("Backdrop", story.CREAM, rough=0.85, emission=story.CREAM, strength=0.18))

    # Desk: light oak top on the cream floor.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, 0.0, -0.018))
    desk = bpy.context.active_object
    desk.name = "desk"
    desk.scale = (1.0, 1.9, 0.036)
    bev = desk.modifiers.new("bevel", "BEVEL")
    bev.width = 0.004
    bev.segments = 3
    assign(desk, oak())
    for x in (-0.42, 0.42):
        for y in (-0.85, 0.85):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.72, location=(x, y, -0.4))
            assign(bpy.context.active_object, principled("Leg", story.NAVY, rough=0.4, metal=0.3))

    # Laptop with the agent on screen, facing the person.
    lap = empty("laptop", None, story.LAPTOP)
    lap.rotation_euler = (0, 0, math.radians(-15))
    bpy.ops.mesh.primitive_cube_add(size=1)
    base = bpy.context.active_object
    base.scale = (0.22, 0.31, 0.012)
    base.location = (0, 0, 0.006)
    base.parent = lap
    alu = principled("Laptop", (0.55, 0.56, 0.6, 1), rough=0.3, metal=1.0)
    assign(base, alu)
    lid = empty("lid", lap, (-0.11, 0, 0.012))
    lid.rotation_euler = (0, math.radians(-18), 0)
    bpy.ops.mesh.primitive_cube_add(size=1)
    shell = bpy.context.active_object
    shell.scale = (0.006, 0.31, 0.21)
    shell.location = (-0.003, 0, 0.105)
    shell.parent = lid
    assign(shell, alu)
    bpy.ops.mesh.primitive_plane_add(size=1)
    scr = bpy.context.active_object
    scr.scale = (0.29, 0.181, 1)
    scr.rotation_euler = (math.radians(90), 0, math.radians(90))
    scr.location = (0.0005, 0, 0.107)
    scr.parent = lid
    img = bpy.data.images.load(str(assets / "laptop.png"))
    scr.data.materials.append(screen_material("Laptop screen", img, 2.0))

    # Mug and a notebook for scale.
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.095, location=(0.3, -0.42, 0.0475))
    mug = bpy.context.active_object
    mug.modifiers.new("bevel", "BEVEL").width = 0.003
    assign(mug, principled("Mug", story.TEAL, rough=0.25, coat=0.5))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.007,
                                     location=(0.3, -0.37, 0.05), rotation=(math.radians(90), 0, 0))
    assign(bpy.context.active_object, MATS["Mug"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.05, -0.55, 0.006))
    book = bpy.context.active_object
    book.scale = (0.21, 0.15, 0.012)
    book.rotation_euler = (0, 0, math.radians(12))
    book.modifiers.new("bevel", "BEVEL").width = 0.002
    assign(book, principled("Notebook", story.GOLD, rough=0.7))


def oak():
    m = principled("Oak", "#d9b98c", rough=0.38, coat=0.25)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 14.0, 1.0)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 2.0
    wave.inputs["Distortion"].default_value = 1.5
    wave.inputs["Detail"].default_value = 2.0
    wave.inputs["Detail Scale"].default_value = 0.6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hex_rgb("#d4b182")
    ramp.color_ramp.elements[1].color = hex_rgb("#e4c79c")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def screen_material(name, img, strength=1.0, sequence_frames=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Coat Weight"].default_value = 0.0
    b.inputs["Specular IOR Level"].default_value = 0.15  # glass, but the picture must win
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Cubic"
    if sequence_frames:
        img.source = "SEQUENCE"
        tex.image_user.frame_duration = sequence_frames
        tex.image_user.frame_start = 1
        tex.image_user.frame_offset = -1
        tex.image_user.use_auto_refresh = True
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return m


# ---------------------------------------------------------------- the phone screen and sensors


SCREEN_POS = Vector((0.04875, -0.0001, 0.00734))   # in the roll joint, from the MuJoCo stand-in
SCREEN_HALF = (0.0699, 0.0323)
FRONT_CAM = Vector((0.0488, 0.061, 0.0073))       # notch on the viewer's right (as on the desk)
BACK_CAM = Vector((0.0405, 0.055, -0.020))


def build_screen(roll, screen_dir: Path):
    bpy.ops.mesh.primitive_plane_add(size=1)
    scr = bpy.context.active_object
    scr.name = "phone screen"
    scr.parent = roll
    scr.scale = (SCREEN_HALF[0] * 2, SCREEN_HALF[1] * 2, 1)
    # plane normal +z -> +x; plane +x (u) -> +y (viewer's right), plane +y (v) -> +z
    scr.rotation_euler = Euler((math.radians(90), 0, math.radians(90)), "XYZ")
    scr.location = SCREEN_POS
    first = min(screen_dir.glob("*.png"))
    img = bpy.data.images.load(str(first))
    scr.data.materials.append(screen_material("Phone screen", img, 2.4, story.FRAMES))
    return scr


def frustum(name, parent, apex: Vector, direction: Vector, up: Vector, fov_h, fov_v, length, color,
            alpha):
    d = direction.normalized()
    right = d.cross(up).normalized()
    u = right.cross(d).normalized()
    hw, hh = math.tan(math.radians(fov_h / 2)) * length, math.tan(math.radians(fov_v / 2)) * length
    c = apex + d * length
    corners = [c + right * sx * hw + u * sy * hh for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([apex, *corners], [], [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)])
    # Only the edges and the far rectangle: a filled cone hides what the camera looks at.
    edges = link(bpy.data.objects.new(name + " edges", mesh))
    edges.parent = parent
    wf = edges.modifiers.new("wire", "WIREFRAME")
    wf.thickness = 0.0014
    assign(edges, glow(name + " line", color, 5.0))
    return [edges]


def arrow(name, parent, origin: Vector, direction: Vector, length, color):
    d = direction.normalized()
    rot = Vector((0, 0, 1)).rotation_difference(d)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0016, depth=length * 0.8)
    shaft = bpy.context.active_object
    shaft.name = name
    shaft.parent = parent
    shaft.rotation_mode = "QUATERNION"
    shaft.rotation_quaternion = rot
    shaft.location = origin + d * length * 0.4
    bpy.ops.mesh.primitive_cone_add(radius1=0.0055, depth=0.014)
    tip = bpy.context.active_object
    tip.parent = parent
    tip.rotation_mode = "QUATERNION"
    tip.rotation_quaternion = rot
    tip.location = origin + d * (length * 0.8 + 0.007)
    for o in (shaft, tip):
        assign(o, glow(name + " glow", color, 5.0))
    return [shaft, tip]


def animate_joints(joints, total, every):
    for n in range(0, total, every):
        f = story.frame(n)
        for name, (pivot, axis) in joints.items():
            pivot.rotation_quaternion = Quaternion(axis, f.joints.get(name, 0.0))
            pivot.keyframe_insert("rotation_quaternion", frame=frame_no(n))


def build_person():
    root = empty("person")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24)
    head = bpy.context.active_object
    head.name = "person head"
    head.scale = (0.085, 0.075, 0.105)
    head.parent = root
    assign(head, principled("Skin", "#e3b48f", rough=0.55, sss=0.2))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24)
    hair = bpy.context.active_object
    hair.scale = (0.09, 0.08, 0.075)
    hair.location = (-0.012, 0, 0.035)
    hair.parent = root
    assign(hair, principled("Hair", "#2b211c", rough=0.6))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.09, location=(0, 0, -0.12))
    neck = bpy.context.active_object
    neck.parent = root
    assign(neck, MATS["Skin"])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24)
    torso = bpy.context.active_object
    torso.name = "person torso"
    torso.scale = (0.13, 0.23, 0.26)
    torso.location = (0.02, 0, -0.38)
    torso.parent = root
    assign(torso, principled("Sweater", story.NAVY, rough=0.85))
    for o in (head, hair, torso):
        for p in o.data.polygons:
            p.use_smooth = True
    return root


def animate_person(root, total, every):
    for n in range(0, total, every):
        f = story.frame(n)
        x, y, z = f.person
        root.location = (x, y, z)
        # face the head
        root.rotation_euler = (0, 0, math.atan2(story.HEAD[1] - y, story.HEAD[0] - x))
        root.keyframe_insert("location", frame=frame_no(n))
        root.keyframe_insert("rotation_euler", frame=frame_no(n))


def face_bracket(person_root):
    """Teal corner brackets around the tracked face (what the front camera locks on)."""
    objs = []
    s = 0.13
    for sx in (-1, 1):
        for sz in (-1, 1):
            for horiz in (True, False):
                bpy.ops.mesh.primitive_cube_add(size=1)
                o = bpy.context.active_object
                o.parent = person_root
                o.scale = (0.002, 0.04 if horiz else 0.003, 0.003 if horiz else 0.04)
                o.location = (0.11, sx * (s / 2 - (0.02 if horiz else 0)), sz * (s * 0.62 - (0 if horiz else 0.02)))
                o.location.y = sx * (s / 2 - 0.02) if horiz else sx * s / 2
                o.location.z = sz * s * 0.62 if horiz else sz * (s * 0.62 - 0.02)
                assign(o, glow("bracket", story.TEAL, 6.0))
                objs.append(o)
    return objs


def sound_rings(name, parent, origin: Vector, scene: str, color, total, travel=0.2):
    """Rings that grow and travel along the parent's +x: a voice going out (the speaker) or
    coming in (the microphone)."""
    objs = []
    rng = next(iter(scene_range(scene)))
    for i in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.05)
        ring = bpy.context.active_object
        ring.name = f"sound {name} {i}"
        ring.parent = parent
        ring.rotation_euler = (0, math.radians(90), 0)  # the ring stands across +x
        m = glow(f"sound {name} {i}", color, 4.0, 0.9)
        assign(ring, m)
        fade = m.node_tree.nodes["Mix Shader"].inputs["Fac"]  # fade out, not down to a dark ring
        for n in range(rng[0], rng[1] + 1, 2):
            u = ((n - rng[0]) / story.FPS * 0.9 + i / 3) % 1.0
            r = 0.012 + u * 0.035
            ring.scale = (r, r, r)
            ring.location = origin + Vector((u * travel, 0, 0))
            ring.keyframe_insert("scale", frame=frame_no(n))
            ring.keyframe_insert("location", frame=frame_no(n))
            fade.default_value = 0.95 * (1 - u) ** 1.5
            fade.keyframe_insert("default_value", frame=frame_no(n))
        constant_interp(ring)
        key_visible(ring, [rng], total)
        objs.append(ring)
    return objs


def compass_ring(total):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.0018, location=(0.0, 0.019, 0.0015))
    ring = bpy.context.active_object
    assign(ring, glow("compass", story.CORAL, 5.0))
    objs = [ring]
    for k in range(36):
        a = math.radians(k * 10)
        long = k % 9 == 0
        bpy.ops.mesh.primitive_cube_add(size=1)
        t = bpy.context.active_object
        t.scale = (0.022 if long else 0.010, 0.0016, 0.001)
        t.rotation_euler = (0, 0, a)
        t.location = (math.cos(a) * (0.17 + (0.016 if long else 0.008)),
                      0.019 + math.sin(a) * (0.17 + (0.016 if long else 0.008)), 0.0015)
        assign(t, glow("north" if k == 0 else "compass", story.GOLD if k == 0 else story.CORAL, 6.0))
        objs.append(t)
    rng = scene_range("camera", "sensors")
    for o in objs:
        key_visible(o, rng, total)
    return objs


def room_points(seed, count, floor_box=None):
    """Feature points on the backdrop and the desk, or on the backdrop and a patch of floor."""
    random.seed(seed)
    pts = []
    for _ in range(count):
        kind = random.random()
        if kind < 0.4:    # backdrop wall
            p = Vector((-1.25 - random.random() * 0.4, random.uniform(-1.6, 1.6), random.uniform(0.0, 1.3)))
        elif kind < 0.75 and floor_box is None:  # desk surface
            p = Vector((random.uniform(-0.48, 0.3), random.uniform(-0.9, 0.9), 0.001))
        else:             # floor
            (x0, x1), (y0, y1) = floor_box or ((-1.2, 0.8), (-1.6, 1.6))
            p = Vector((random.uniform(x0, x1), random.uniform(y0, y1), -0.759))
        pts.append(p)
    return pts


def feature_points(cam_obj, forward: Vector, scene: str, pts, total, reach=3.0):
    """ARKit-style feature points that light up where a back camera has looked."""
    rng = scene_range(scene)[0]
    seen_at = [None] * len(pts)
    sc = bpy.context.scene
    for n in range(rng[0], rng[1], 2):
        sc.frame_set(frame_no(n))
        mw = cam_obj.matrix_world
        origin = mw.translation
        fwd = (mw.to_3x3() @ forward).normalized()
        for i, p in enumerate(pts):
            if seen_at[i] is None:
                d = p - origin
                if d.length < reach and d.normalized().dot(fwd) > math.cos(math.radians(34)):
                    seen_at[i] = n
    mesh = bpy.data.meshes.get("dot")
    if mesh is None:
        import bmesh
        mesh = bpy.data.meshes.new("dot")
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0055)
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(glow("feature", story.GOLD, 8.0))
    objs = []
    for i, p in enumerate(pts):
        if seen_at[i] is None:
            continue
        o = link(bpy.data.objects.new(f"pt {scene} {i}", mesh))
        o.location = p
        key_visible(o, [(seen_at[i], rng[1])], total)
        objs.append(o)
    return objs


# ---------------------------------------------------------------- Open Duck Mini, walking


DUCK_ORIGIN = Vector((1.4, -1.9, -0.76))  # where the recorded walk starts, on the studio floor
DUCK_YAW = math.radians(60)


def duck_material(mesh: str):
    if "iphone" in mesh:
        return principled("iPhone", "#0c0d10", rough=0.22, metal=0.6, coat=0.6)
    if "servo" in mesh or "wj-wk00" in mesh:
        return principled("Servo", "#141416", rough=0.55)
    if "palonier" in mesh:
        return principled("Horn", (0.62, 0.62, 0.64, 1), rough=0.3, metal=1.0)
    if "lager" in mesh:
        return principled("Steel", (0.62, 0.62, 0.64, 1), rough=0.22, metal=1.0)
    if "tpu" in mesh:
        return principled("TPU", "#1d1b22", rough=0.8)
    return pla("PLA red", RED)


class Duck:
    """The recorded walk: objects keyed per frame, and the phone's path for the camera."""

    def __init__(self, path: Path, total: int):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.frames = data["frames"]
        self.a, self.b = scene_range("walk")[0]
        self.root = empty("duck", None, DUCK_ORIGIN)
        self.root.rotation_euler = (0, 0, DUCK_YAW)
        self.world = Matrix.Translation(DUCK_ORIGIN) @ Matrix.Rotation(DUCK_YAW, 4, "Z")
        self.objs = {}
        for i, m in enumerate(data["meshes"]):
            if m["file"]:
                o = link(bpy.data.objects.new("duck " + m["mesh"], import_stl(Path(m["file"]), 1.0)))
                assign(o, duck_material(m["mesh"]))
                smooth_auto(o)
            else:
                o = empty("duck " + m["mesh"])
            o.parent = self.root
            o.rotation_mode = "QUATERNION"
            # Left and right use the same STL (and every servo the same three): key by index too.
            key = m["mesh"] if m["mesh"] not in self.objs else f"{m['mesh']} {i}"
            self.objs[key] = (i, o)
        for n in range(self.a, self.b + 1):
            row = self.row(n)
            for i, o in self.objs.values():
                x, y, z, qw, qx, qy, qz = row[i]
                o.location = (x, y, z)
                o.rotation_quaternion = Quaternion((qw, qx, qy, qz))
                o.keyframe_insert("location", frame=frame_no(n))
                o.keyframe_insert("rotation_quaternion", frame=frame_no(n))
        size = data["meshes"][self.objs["screen"][0]]["size"]
        visible = [o for _, o in self.objs.values()] + [self.screen_plane(size)]
        for o in visible:
            key_visible(o, [(self.a, self.b)], total)

    def row(self, n):
        return self.frames[max(0, min(len(self.frames) - 1, n - self.a))]

    def pose(self, name, n) -> tuple[Vector, Matrix]:
        x, y, z, qw, qx, qy, qz = self.row(n)[self.objs[name][0]]
        m = self.world @ Matrix.LocRotScale(Vector((x, y, z)), Quaternion((qw, qx, qy, qz)), None)
        return m.translation, m.to_3x3()

    def outward(self) -> float:
        """+1 if the screen box's +z faces out of the phone, else -1."""
        p, r = self.pose("screen", self.a)
        rear, _ = self.pose("cam_rear", self.a)
        return 1.0 if (r @ Vector((0, 0, 1))).dot(p - rear) > 0 else -1.0

    def normal(self, n) -> Vector:
        return self.pose("screen", n)[1] @ Vector((0, 0, self.outward()))

    def phone(self, n) -> Vector:
        return self.pose("screen", n)[0]

    def screen_plane(self, size):
        bpy.ops.mesh.primitive_plane_add(size=1)
        scr = bpy.context.active_object
        scr.name = "duck phone screen"
        scr.parent = self.objs["screen"][1]
        scr.scale = (size[0] * 2, size[1] * 2, 1)
        s = self.outward()
        scr.location = (0, 0, s * (size[2] + 0.0004))
        if s < 0:
            scr.rotation_euler = (math.radians(180), 0, 0)
        scr.data.materials.append(bpy.data.materials["Phone screen"])
        return scr

    def rear_forward(self) -> Vector:
        """The back camera's view direction in the cam_rear empty's own frame."""
        _, r = self.pose("cam_rear", self.a)
        return (r.transposed() @ -self.normal(self.a)).normalized()

    def rear_up(self) -> Vector:
        _, r = self.pose("cam_rear", self.a)
        _, rs = self.pose("screen", self.a)
        return (r.transposed() @ (rs @ Vector((0, 1, 0)))).normalized()


def arkit_trail(duck: Duck, total):
    """The path ARKit reports, drawn on the floor as the robot walks, and the world origin."""
    cu = bpy.data.curves.new("arkit trail", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.0045
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    raw = [duck.phone(n) for n in range(duck.a, duck.b + 1)]
    # ARKit reports the phone, which sways with every step; the map shows the walk (a 0.5 s mean).
    pts = [sum(raw[max(0, k - 7):k + 8], Vector()) / len(raw[max(0, k - 7):k + 8]) for k in range(len(raw))]
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts, strict=True):
        p.co = (v.x, v.y, -0.757, 1)
    trail = link(bpy.data.objects.new("arkit trail", cu))
    assign(trail, glow("trail", story.GOLD, 2.2))  # brighter washes out to cream
    with contextlib.suppress(*API_DRIFT):
        cu.bevel_factor_mapping_end = "SEGMENTS"
    cu.bevel_factor_end = 0.0
    cu.keyframe_insert("bevel_factor_end", frame=frame_no(duck.a))
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=frame_no(duck.b))
    for fc in _fcurves(cu.animation_data.action):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    objs = [trail]
    start = Vector((pts[0].x, pts[0].y, -0.756))
    heading = duck.normal(duck.a)
    heading.z = 0
    heading.normalize()
    left = Vector((-heading.y, heading.x, 0))
    for name, d, c in (("origin fwd", heading, story.CORAL), ("origin left", left, story.TEAL),
                       ("origin up", Vector((0, 0, 1)), story.GOLD)):
        objs += arrow(name, None, start, d, 0.12, c)
    for o in objs:
        key_visible(o, [(duck.a, duck.b)], total)
    return objs


def data_stream(phone_obj, total):
    """Packets flying from the phone to the laptop while the agent reads the sensors."""
    rng = scene_range("sensors")[0]
    scene = bpy.context.scene
    end = Vector((story.LAPTOP[0] - 0.08, story.LAPTOP[1], 0.14))
    mat = glow("packet", story.CORAL, 9.0)
    objs = []
    for i in range(10):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0055, segments=16, ring_count=8)
        o = bpy.context.active_object
        assign(o, mat)
        objs.append(o)
    for n in range(rng[0], rng[1] + 1, 2):
        scene.frame_set(frame_no(n))
        start = phone_obj.matrix_world.translation.copy()
        for i, o in enumerate(objs):
            u = ((n - rng[0]) / story.FPS * 0.7 + i / len(objs)) % 1.0
            mid = (start + end) / 2 + Vector((0.05, 0, 0.16))
            p = (1 - u) ** 2 * start + 2 * (1 - u) * u * mid + u ** 2 * end
            o.location = p
            o.keyframe_insert("location", frame=frame_no(n))
    for o in objs:
        key_visible(o, [rng], total)
    return objs


# ---------------------------------------------------------------- camera and light


SHOTS = {  # scene: [(t within scene 0..1, camera position, look at, lens)]
    "intro": [(0, (1.15, -1.05, 0.55), (0.04, 0.0, 0.25), 45), (1, (0.85, -0.42, 0.36), (0.06, 0.0, 0.27), 55)],
    "follow": [(0, (1.25, 0.6, 1.0), (0.06, 0.0, 0.27), 55), (1, (1.2, 0.3, 0.95), (0.06, 0.0, 0.27), 55)],
    "listen": [(0, (0.40, -1.05, 0.52), (0.36, 0.02, 0.36), 35), (1, (0.30, -0.95, 0.48), (0.34, 0.02, 0.35), 38)],
    "talk": [(0, (0.95, -0.8, 0.42), (0.04, -0.12, 0.2), 45), (1, (0.85, -0.62, 0.38), (0.04, -0.1, 0.22), 50)],
    "sensing": [(0, (-0.25, -1.45, 1.0), (-0.1, 0.0, 0.25), 30), (1, (0.75, -1.45, 0.95), (-0.1, 0.0, 0.25), 30)],
    "camera": [(0, (0.52, -0.06, 0.31), (0.07, 0.0, 0.29), 55), (1, (0.44, 0.04, 0.30), (0.07, 0.0, 0.29), 55)],
    "sensors": [(0, (1.05, -0.75, 0.72), (0.08, 0.15, 0.2), 32), (1, (0.95, -0.3, 0.78), (0.08, 0.15, 0.2), 32)],
    # The cockpit scene shows a browser over this view, blurred (compose.py).
    "cockpit": [(0, (0.95, -0.3, 0.78), (0.08, 0.15, 0.2), 32), (1, (0.95, -0.3, 0.78), (0.08, 0.15, 0.2), 32)],
    "end": [(0, (0.95, -0.45, 0.38), (0.06, 0.0, 0.27), 50), (1, (1.25, -0.62, 0.44), (0.06, 0.0, 0.25), 50)],
}


def build_camera(total, duck=None):
    cam_data = bpy.data.cameras.new("cam")
    cam = link(bpy.data.objects.new("camera", cam_data))
    target = empty("cam target")
    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 2.8
    cam_data.sensor_width = 36
    bpy.context.scene.camera = cam
    def key(n, pos, look, lens):
        cam.location = pos
        target.location = look
        cam_data.lens = lens
        cam.keyframe_insert("location", frame=frame_no(n))
        target.keyframe_insert("location", frame=frame_no(n))
        cam_data.keyframe_insert("lens", frame=frame_no(n))

    head = Vector(story.HEAD)
    for s in story.SCENES:
        a, b = int(s.start * story.FPS), int(s.end * story.FPS) - 1
        if s.key == "walk" and duck:
            # Follow the walking robot from ahead and to its side, so the face and the trail show.
            heading = 0.0
            for n in list(range(a, b, 3)) + [b]:
                p = duck.phone(n)
                h = duck.normal(n)
                # the heading, smoothed: the head looks around while the body walks on
                want = math.atan2(h.y, h.x)
                heading = want if n == a else heading + 0.08 * math.remainder(want - heading, math.tau)
                u = (n - a) / max(1, b - a)
                ang = heading + math.radians(48 - 18 * u)
                pos = p + Vector((math.cos(ang) * 1.0, math.sin(ang) * 1.0, 0.16 - 0.04 * u))
                key(n, pos, p + Vector((0, 0, -0.12)), 36)
        elif s.key in FACING:
            # Shots that must see the screen: from the person's side, wherever they are.
            reach, side, up, lens, look = FACING[s.key]
            for n in list(range(a, b, 3)) + [b]:
                p = Vector(story.frame(n).person)
                d = (p - head)
                d.z = 0
                d.normalize()
                lateral = Vector((-d.y, d.x, 0))
                u = (n - a) / max(1, b - a)
                pos = head + d * (reach - 0.06 * u) + lateral * side + Vector((0, 0, up))
                key(n, pos, head + Vector(look), lens)
        else:
            for u, pos, look, lens in SHOTS[s.key]:
                key(round(a + (b - a) * u), pos, look, lens)
    # Hard cuts between scenes: smooth within a scene, constant across the boundary.
    for owner in (cam, target, cam_data):
        for fc in _fcurves(owner.animation_data.action):
            pts = list(fc.keyframe_points)
            for i, k in enumerate(pts):
                k.interpolation = "BEZIER"
                k.easing = "AUTO"
                if i + 1 < len(pts):
                    here = story.scene_at((k.co.x - 1) / story.FPS).key
                    nxt = story.scene_at((pts[i + 1].co.x - 1) / story.FPS).key
                    if here != nxt:
                        k.interpolation = "CONSTANT"
    return cam


FACING = {  # scene: (distance from the head towards the person, sideways, up, lens, look offset)
    "talk": (0.75, -0.32, 0.12, 40, (0.0, -0.06, -0.06)),
    "camera": (0.36, -0.05, 0.03, 45, (0.02, 0.0, 0.0)),
}


def build_lights():
    world = bpy.context.scene.world or bpy.data.worlds.new("world")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hex_rgb(story.CREAM_2)
    bg.inputs["Strength"].default_value = 0.15
    # Where the camera sees past the backdrop it should see cream, not the dim fill light.
    nt = world.node_tree
    seen = nt.nodes.new("ShaderNodeBackground")
    seen.inputs["Color"].default_value = hex_rgb(story.CREAM)
    seen.inputs["Strength"].default_value = 0.9
    path = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes["World Output"]
    nt.links.new(path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(seen.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])

    def area(name, loc, look, power, size, color):
        d = bpy.data.lights.new(name, "AREA")
        d.energy = power
        d.size = size
        d.color = hex_rgb(color)[:3]
        o = link(bpy.data.objects.new(name, d))
        o.location = loc
        direction = Vector(look) - Vector(loc)
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        return o

    area("key", (1.2, -1.1, 1.5), (0.05, 0, 0.25), 110, 1.0, "#fff1dc")
    area("fill", (1.0, 1.3, 0.7), (0.05, 0, 0.25), 25, 1.5, "#dfe9ff")
    area("rim", (-0.9, 0.5, 1.2), (0.05, 0, 0.3), 140, 0.5, "#ffe2c6")
    area("top", (0.0, 0.0, 2.2), (0.0, 0.0, 0.0), 30, 2.0, "#ffffff")
    area("walk key", (2.7, -2.3, 0.8), (1.5, -1.3, -0.55), 160, 1.2, "#fff1dc")  # the duck's floor


def setup_render(scale, samples):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.resolution_x, sc.render.resolution_y = story.SIZE
    sc.render.resolution_percentage = scale
    sc.render.fps = story.FPS
    sc.frame_start, sc.frame_end = 1, story.FRAMES
    ee = sc.eevee
    for attr, val in (("taa_render_samples", samples), ("use_raytracing", True),
                      ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8),
                      ("use_gtao", True), ("fast_gi_method", "GLOBAL_ILLUMINATION"),
                      ("use_fast_gi", True)):
        if hasattr(ee, attr):
            with contextlib.suppress(*API_DRIFT):
                setattr(ee, attr, val)
    if hasattr(ee, "ray_tracing_options"):
        with contextlib.suppress(*API_DRIFT):
            ee.ray_tracing_options.resolution_scale = "1"
            ee.ray_tracing_options.use_denoise = True
    vs = sc.view_settings
    with contextlib.suppress(*API_DRIFT):
        vs.view_transform = "AgX"
        vs.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False


# ---------------------------------------------------------------- main


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--rig", type=Path, required=True)
    p.add_argument("--screen", type=Path, required=True)
    p.add_argument("--assets", type=Path, required=True)
    p.add_argument("--duck", type=Path, required=True, help="the walk duck_walk.py recorded")
    p.add_argument("--out", type=Path)
    p.add_argument("--frames", default=None, help="a:b story frames, or a,b,c")
    p.add_argument("--scale", type=int, default=100)
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--save", type=Path)
    args = p.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    total = story.FRAMES
    setup_render(args.scale, args.samples)
    joints, sites = build_rig(args.rig)
    animate_joints(joints, total, 1)
    roll = joints["head_roll"][0]
    build_set(args.assets)
    scr = build_screen(roll, args.screen)

    fx = []
    fx += [(o, scene_range("follow", "sensing"))
           for o in frustum("front camera", roll, FRONT_CAM, Vector((1, 0, 0)), Vector((0, 0, 1)),
                            62, 44, 0.42, story.TEAL, 0.05)]
    back = frustum("back camera", roll, BACK_CAM, Vector((-1, 0, 0)), Vector((0, 0, 1)), 66, 50, 0.6,
                   story.GOLD, 0.05)
    fx += [(o, scene_range("sensing")) for o in back]
    imu_parent, imu_pos = sites.get("phone_imu", (roll, Vector((0.0448, 0, 0.0073))))
    axes = []
    for name, d, c in (("imu x", (1, 0, 0), story.CORAL), ("imu y", (0, 1, 0), story.TEAL),
                       ("imu z", (0, 0, 1), story.GOLD)):
        axes += arrow(name, imu_parent, imu_pos + Vector((0.004, 0, 0)), Vector(d), 0.075, c)
    fx += [(o, scene_range("sensing", "sensors")) for o in axes]
    for o, rng in fx:
        key_visible(o, rng, total)

    person = build_person()
    animate_person(person, total, 1)
    for o in face_bracket(person):
        key_visible(o, scene_range("follow", "sensing"), total)

    # The voice: in from the person's mouth while listening, out of the phone while talking.
    sound_rings("mic", person, Vector((0.075, 0, -0.045)), "listen", story.TEAL, total, travel=0.22)
    sound_rings("speaker", roll, SCREEN_POS + Vector((0.006, 0, 0)), "talk", story.CORAL, total, travel=0.18)
    compass_ring(total)

    back_cam = empty("back cam point", roll, BACK_CAM)
    feature_points(back_cam, Vector((-1, 0, 0)), "sensing", room_points(4, 320), total)

    duck = Duck(args.duck, total)
    rear = duck.objs["cam_rear"][1]
    for o in frustum("duck back camera", rear, Vector(), duck.rear_forward(), duck.rear_up(), 66, 50, 0.3,
                     story.GOLD, 0.05):
        key_visible(o, scene_range("walk"), total)
    arkit_trail(duck, total)
    feature_points(rear, duck.rear_forward(), "walk", room_points(9, 420, ((0.5, 2.8), (-2.6, 1.0))), total)
    data_stream(scr, total)
    build_camera(total, duck)
    build_lights()

    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=str(args.save.resolve()))
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        sc = bpy.context.scene
        if args.frames and "," in args.frames:
            frames = [int(v) for v in args.frames.split(",")]
        else:
            a, b = (args.frames or f"0:{total}").split(":")
            frames = range(int(a), int(b))
        for n in frames:
            sc.frame_set(frame_no(n))
            sc.render.filepath = str((args.out / f"{n:05d}.png").resolve())
            bpy.ops.render.render(write_still=True)
            print(f"rendered {n}", flush=True)


main()
