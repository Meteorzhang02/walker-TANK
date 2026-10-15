# Rebuilds the ammo_crate asset (CHANGE-BRIEF.md, Asset 2) from an empty scene.
#
# These are the execute_blender_code bodies sent to the live Blender session over MCP, in
# order; all of them succeeded on the first send. The join and the rotation/scale apply use
# no operators (bmesh join, mesh.transform), so there is no select_set on a stale view-layer
# entry as in cover_wall step 6. The stripe is 0.83 m deep, not the lid's 0.84 m, so its ends
# are not coplanar with the lid's front and back faces. The bounding box is 1.24 x 0.84 x
# 0.71 m (lid overhang + stripe), +0.04/+0.04/+0.01 m over the brief, within its +/-0.1 m.
# The save of the live session is not included: this script never saves a .blend file and
# does not export.
#
# Run:
#   "D:\blender\blender.exe" -b --factory-startup --python-exit-code 1 ^
#       --python tools/blender/build_ammo_crate.py

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

# --- Step 2: flat-colour materials (Principled BSDF base colour only). --------------------
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

m_body = make_material("M_CrateBody", "#4B5320")
m_lid = make_material("M_CrateLid", "#3D441A")
m_stripe = make_material("M_CrateStripe", "#E8E6DF")
for m in (m_body, m_lid, m_stripe):
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    print(m.name, [round(v, 4) for v in bsdf.inputs["Base Color"].default_value])

# --- Step 3: ammo_crate_body, 1.2 x 0.8 x 0.6 m, underside centre at the world origin. -----
import bpy, bmesh

def make_box(name, size, base_centre, material):
    sx, sy, sz = size
    bx, by, bz = base_centre
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = bx + v.co.x * sx
        v.co.y = by + v.co.y * sy
        v.co.z = bz + (v.co.z + 0.5) * sz
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

body = make_box("ammo_crate_body", (1.2, 0.8, 0.6), (0.0, 0.0, 0.0),
                bpy.data.materials["M_CrateBody"])
print(body.name, "faces:", len(body.data.polygons), "verts:", len(body.data.vertices))

# --- Step 4: ammo_crate_lid, 1.24 x 0.84 x 0.1 m, z 0.6..0.7 (0.02 m overhang each side). --
import bpy, bmesh

def make_box(name, size, base_centre, material):
    sx, sy, sz = size
    bx, by, bz = base_centre
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = bx + v.co.x * sx
        v.co.y = by + v.co.y * sy
        v.co.z = bz + (v.co.z + 0.5) * sz
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

lid = make_box("ammo_crate_lid", (1.24, 0.84, 0.1), (0.0, 0.0, 0.6),
               bpy.data.materials["M_CrateLid"])
print(lid.name, "faces:", len(lid.data.polygons), "verts:", len(lid.data.vertices))

# --- Step 5: ammo_crate_stripe, 0.15 x 0.83 x 0.01 m, y -0.415..0.415 (front to back),
# z 0.70..0.71, centred on the lid. ----------------------------------------------------------
import bpy, bmesh

def make_box(name, size, base_centre, material):
    sx, sy, sz = size
    bx, by, bz = base_centre
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = bx + v.co.x * sx
        v.co.y = by + v.co.y * sy
        v.co.z = bz + (v.co.z + 0.5) * sz
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

stripe = make_box("ammo_crate_stripe", (0.15, 0.83, 0.01), (0.0, 0.0, 0.7),
                  bpy.data.materials["M_CrateStripe"])
ys = [v.co.y for v in stripe.data.vertices]
zs = [v.co.z for v in stripe.data.vertices]
print(stripe.name, "faces:", len(stripe.data.polygons), "verts:", len(stripe.data.vertices),
      "y:", round(min(ys), 4), round(max(ys), 4), "z:", round(min(zs), 4), round(max(zs), 4))

# --- Step 6a: join the three cubes into one mesh object 'ammo_crate' without operators
# (three material slots, origin at the centre of the underside = world origin). -----------
import bpy, bmesh

parts = [bpy.data.objects[n] for n in ("ammo_crate_body", "ammo_crate_lid", "ammo_crate_stripe")]
mats = [bpy.data.materials[n] for n in ("M_CrateBody", "M_CrateLid", "M_CrateStripe")]

bm = bmesh.new()
for ob in parts:
    slot = mats.index(ob.data.materials[0])
    tmp = bmesh.new()
    tmp.from_mesh(ob.data)
    tmp.transform(ob.matrix_world)
    for f in tmp.faces:
        f.material_index = slot
    me_tmp = bpy.data.meshes.new("tmp")
    tmp.to_mesh(me_tmp)
    tmp.free()
    bm.from_mesh(me_tmp)
    bpy.data.meshes.remove(me_tmp)

me = bpy.data.meshes.new("ammo_crate")
bm.to_mesh(me)
bm.free()
for m in mats:
    me.materials.append(m)

for ob in parts:
    old = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(old)

crate = bpy.data.objects.new("ammo_crate", me)
bpy.context.scene.collection.objects.link(crate)
crate.location = (0.0, 0.0, 0.0)
bpy.context.view_layer.update()
print("joined:", crate.name, "faces:", len(me.polygons), "verts:", len(me.vertices),
      "slots:", [s.material.name for s in crate.material_slots])
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])

# --- Step 6b: apply rotation and scale on ammo_crate without operators, then check against
# CHANGE-BRIEF.md (bounding box 1.24 x 0.84 x 0.71 m). -------------------------------------
import bpy
from mathutils import Matrix

view_layer = bpy.context.view_layer
view_layer.update()
crate = bpy.data.objects["ammo_crate"]
me = crate.data

# Apply rotation and scale without operators: bake them into the mesh, then reset.
loc, rot, scl = crate.matrix_basis.decompose()
rot_scale = rot.to_matrix().to_4x4() @ Matrix.Diagonal((*scl, 1.0))
me.transform(rot_scale)
me.update()
crate.rotation_mode = "XYZ"
crate.rotation_euler = (0.0, 0.0, 0.0)
crate.scale = (1.0, 1.0, 1.0)
view_layer.update()
view_layer.objects.active = crate

xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
zs = [v.co.z for v in me.vertices]
size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
slots = [s.material.name for s in crate.material_slots]
errors = []
if any(abs(a - b) > 1e-4 for a, b in zip(size, (1.24, 0.84, 0.71))):
    errors.append(f"size {size}")
if abs(min(zs)) > 1e-4:
    errors.append(f"lowest z {min(zs)}")
if abs((max(xs) + min(xs)) / 2) > 1e-4 or abs((max(ys) + min(ys)) / 2) > 1e-4:
    errors.append("origin not at underside centre")
if tuple(crate.location) != (0.0, 0.0, 0.0):
    errors.append(f"location {tuple(crate.location)}")
if tuple(crate.rotation_euler) != (0.0, 0.0, 0.0) or tuple(crate.scale) != (1.0, 1.0, 1.0):
    errors.append("rotation/scale not applied")
if tris > 60:
    errors.append(f"{tris} triangles > 60")
if len(crate.modifiers):
    errors.append("modifiers present")
if slots != ["M_CrateBody", "M_CrateLid", "M_CrateStripe"]:
    errors.append(f"slots {slots}")
mesh_objects = [o.name for o in bpy.data.objects if o.type == "MESH"]
if mesh_objects != ["ammo_crate"]:
    errors.append(f"mesh objects {mesh_objects}")

brief = (1.2, 0.8, 0.7)
print("size:", tuple(round(s, 4) for s in size), "lowest z:", round(min(zs), 4))
print("difference from brief 1.2 x 0.8 x 0.7:",
      tuple(round(s - b, 4) for s, b in zip(size, brief)), "(tolerance +/-0.1 m)")
if any(abs(s - b) > 0.1 for s, b in zip(size, brief)):
    errors.append("outside brief tolerance")
print("triangles:", tris, "faces:", len(me.polygons), "verts:", len(me.vertices))
print("slots:", slots, "faces per slot:",
      [sum(1 for p in me.polygons if p.material_index == i) for i in range(len(slots))])
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])
if errors:
    raise RuntimeError("ammo_crate checks failed: " + "; ".join(errors))
print("ammo_crate checks passed")
