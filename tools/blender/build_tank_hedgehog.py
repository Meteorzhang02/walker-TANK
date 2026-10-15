# Rebuilds the tank_hedgehog asset (CHANGE-BRIEF.md, Asset 3) from an empty scene.
#
# These are the execute_blender_code bodies sent to the live Blender session over MCP, in
# order; all of them succeeded on the first send. Beams are 2.125 m, not the brief's original
# 2.4 m (CHANGE-BRIEF.md, Revisions 2026-10-15): 2.4 m beams give 2.011 x 2.011 x 1.559 m,
# 0.009 m over the height tolerance, because the original numbers used beam centrelines.
# The beams lie on local X, Y, Z (plain orientation), are tilted by the shortest-arc rotation
# that turns local (1,1,1) to world +Z so the group stands on three beam ends, and with no
# extra yaw the footprint is square. The bounding box is 1.794 x 1.794 x 1.400 m, -0.106 /
# -0.106 / +0.000 m from the brief's 1.9 x 1.9 x 1.4, within its +/-0.15 m. As with
# ammo_crate, the join and the rotation/scale apply use no operators (bmesh join,
# mesh.transform). The save of the live session is not included: this script never saves a
# .blend file and does not export.
#
# Run:
#   "D:\blender\blender.exe" -b --factory-startup --python-exit-code 1 ^
#       --python tools/blender/build_tank_hedgehog.py

# --- Step 1: empty the scene and set metric units (1 BU = 1 m). ---------------------------
import bpy

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for block in list(coll):
        if block.users == 0:
            coll.remove(block)

us = scene.unit_settings
systems = [i.identifier for i in us.bl_rna.properties["system"].enum_items]
us.system = "METRIC" if "METRIC" in systems else systems[0]
us.scale_length = 1.0
lengths = [i.identifier for i in us.bl_rna.properties["length_unit"].enum_items]
if "METERS" in lengths:
    us.length_unit = "METERS"

print("objects:", len(bpy.data.objects), "meshes:", len(bpy.data.meshes),
      "materials:", len(bpy.data.materials), "lights:", len(bpy.data.lights),
      "cameras:", len(bpy.data.cameras))
print("units:", us.system, us.length_unit, us.scale_length)

# --- Step 2: flat-colour material (Principled BSDF base colour only). ---------------------
import bpy

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def make_material(name, hex_rgb):
    rgb = [int(hex_rgb[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    lin = [srgb_to_linear(c) for c in rgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    mat.diffuse_color = (*lin, 1.0)  # viewport solid colour only
    return mat

m_steel = make_material("M_HedgehogSteel", "#5A4A3F")
bsdf = next(n for n in m_steel.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
print(m_steel.name, [round(v, 4) for v in bsdf.inputs["Base Color"].default_value])

# --- Step 3: three beams 2.125 x 0.15 x 0.15 m on local X, Y, Z, centred at the origin. ----
import bpy, bmesh

BEAM_LENGTH = 2.125
BEAM_SECTION = 0.15

def make_beam(name, axis, material):
    size = [BEAM_SECTION] * 3
    size[axis] = BEAM_LENGTH
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

steel = bpy.data.materials["M_HedgehogSteel"]
for axis, name in enumerate(("hedgehog_beam_x", "hedgehog_beam_y", "hedgehog_beam_z")):
    ob = make_beam(name, axis, steel)
    co = [v.co for v in ob.data.vertices]
    ext = [round(max(c[i] for c in co) - min(c[i] for c in co), 4) for i in range(3)]
    print(ob.name, "faces:", len(ob.data.polygons), "verts:", len(ob.data.vertices), "extent:", ext)

# --- Step 4: tilt the beams so the group stands on three beam ends, lift onto Z = 0. -------
import bpy
from mathutils import Vector

# Shortest-arc rotation that turns local (1,1,1) to world +Z: the three -axis beam ends become
# the feet. With no extra yaw, this makes the footprint square (checked with yaw 0..60 deg
# before building).
tilt = Vector((1.0, 1.0, 1.0)).rotation_difference(Vector((0.0, 0.0, 1.0)))
names = ("hedgehog_beam_x", "hedgehog_beam_y", "hedgehog_beam_z")
for n in names:
    ob = bpy.data.objects[n]
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = tilt.to_euler("XYZ")
bpy.context.view_layer.update()

def world_verts():
    return [bpy.data.objects[n].matrix_world @ v.co for n in names
            for v in bpy.data.objects[n].data.vertices]

lift = -min(p.z for p in world_verts())
for n in names:
    bpy.data.objects[n].location = (0.0, 0.0, lift)
bpy.context.view_layer.update()

pts = world_verts()
size = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
print("tilt euler deg:", [round(a * 57.29578, 3) for a in tilt.to_euler("XYZ")])
print("lift:", round(lift, 4))
print("group size:", [round(s, 4) for s in size], "lowest z:", round(min(p.z for p in pts), 6))
print("verts at z=0:", sum(1 for p in pts if abs(p.z) < 1e-5))

# --- Step 5: join the three beams into one mesh object 'tank_hedgehog' without operators
# (one material slot, origin on the floor under the centre = world origin). ---------------
import bpy, bmesh

names = ("hedgehog_beam_x", "hedgehog_beam_y", "hedgehog_beam_z")
parts = [bpy.data.objects[n] for n in names]
steel = bpy.data.materials["M_HedgehogSteel"]
bpy.context.view_layer.update()

# Join without operators: bake each beam's world matrix (tilt + lift) into one bmesh.
bm = bmesh.new()
for ob in parts:
    tmp = bmesh.new()
    tmp.from_mesh(ob.data)
    tmp.transform(ob.matrix_world)
    for f in tmp.faces:
        f.material_index = 0
    me_tmp = bpy.data.meshes.new("tmp")
    tmp.to_mesh(me_tmp)
    tmp.free()
    bm.from_mesh(me_tmp)
    bpy.data.meshes.remove(me_tmp)

me = bpy.data.meshes.new("tank_hedgehog")
bm.to_mesh(me)
bm.free()
me.materials.append(steel)

for ob in parts:
    old = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(old)

hedgehog = bpy.data.objects.new("tank_hedgehog", me)
bpy.context.scene.collection.objects.link(hedgehog)
hedgehog.location = (0.0, 0.0, 0.0)  # origin on the floor under the centre
bpy.context.view_layer.update()
xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
print("joined:", hedgehog.name, "faces:", len(me.polygons), "verts:", len(me.vertices),
      "slots:", [s.material.name for s in hedgehog.material_slots])
print("bbox centre xy:", round((max(xs) + min(xs)) / 2, 6), round((max(ys) + min(ys)) / 2, 6))
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])

# --- Step 6: apply rotation and scale on tank_hedgehog without operators, then check against
# 1.794 x 1.794 x 1.400 m and against CHANGE-BRIEF.md (1.9 x 1.9 x 1.4, +/-0.15 m). ---------
import bpy
from mathutils import Matrix

view_layer = bpy.context.view_layer
view_layer.update()
hedgehog = bpy.data.objects["tank_hedgehog"]
me = hedgehog.data

# Apply rotation and scale without operators: bake them into the mesh, then reset.
# (The join already baked each beam's tilt into the mesh, so this is expected to be identity.)
loc, rot, scl = hedgehog.matrix_basis.decompose()
rot_scale = rot.to_matrix().to_4x4() @ Matrix.Diagonal((*scl, 1.0))
print("baked rot/scale is identity:", rot_scale == Matrix.Identity(4))
me.transform(rot_scale)
me.update()
hedgehog.rotation_mode = "XYZ"
hedgehog.rotation_euler = (0.0, 0.0, 0.0)
hedgehog.scale = (1.0, 1.0, 1.0)
view_layer.update()
view_layer.objects.active = hedgehog

xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
zs = [v.co.z for v in me.vertices]
size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
feet = sum(1 for z in zs if abs(z) < 1e-4)
slots = [s.material.name for s in hedgehog.material_slots]
errors = []
expected = (1.794, 1.794, 1.400)  # 2.125 m beams, see CHANGE-BRIEF.md Revisions 2026-10-15
if any(abs(a - b) > 1e-3 for a, b in zip(size, expected)):
    errors.append(f"size {size}")
if abs(min(zs)) > 1e-4:
    errors.append(f"lowest z {min(zs)}")
if feet != 3:
    errors.append(f"{feet} vertices at z=0, expected 3")
if abs((max(xs) + min(xs)) / 2) > 1e-4 or abs((max(ys) + min(ys)) / 2) > 1e-4:
    errors.append("origin not at underside centre")
if tuple(hedgehog.location) != (0.0, 0.0, 0.0):
    errors.append(f"location {tuple(hedgehog.location)}")
if tuple(hedgehog.rotation_euler) != (0.0, 0.0, 0.0) or tuple(hedgehog.scale) != (1.0, 1.0, 1.0):
    errors.append("rotation/scale not applied")
if tris > 60:
    errors.append(f"{tris} triangles > 60")
if len(hedgehog.modifiers):
    errors.append("modifiers present")
if slots != ["M_HedgehogSteel"]:
    errors.append(f"slots {slots}")
mesh_objects = [o.name for o in bpy.data.objects if o.type == "MESH"]
if mesh_objects != ["tank_hedgehog"]:
    errors.append(f"mesh objects {mesh_objects}")

brief = (1.9, 1.9, 1.4)
print("size:", tuple(round(s, 4) for s in size), "lowest z:", round(min(zs), 6), "feet:", feet)
print("difference from expected 1.794 x 1.794 x 1.400:",
      tuple(round(s - e, 4) for s, e in zip(size, expected)), "(tolerance 0.001 m)")
print("difference from brief 1.9 x 1.9 x 1.4:",
      tuple(round(s - b, 4) for s, b in zip(size, brief)), "(tolerance +/-0.15 m)")
if any(abs(s - b) > 0.15 for s, b in zip(size, brief)):
    errors.append("outside brief tolerance")
print("triangles:", tris, "faces:", len(me.polygons), "verts:", len(me.vertices))
print("slots:", slots)
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])
if errors:
    raise RuntimeError("tank_hedgehog checks failed: " + "; ".join(errors))
print("tank_hedgehog checks passed")
