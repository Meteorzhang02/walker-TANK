# Rebuilds the cover_wall asset (CHANGE-BRIEF.md, Asset 1) from an empty scene.
#
# These are the execute_blender_code bodies sent to the live Blender session over MCP, in
# order. Step 6 was sent once and failed after the join (stale view-layer entry on deselect);
# the join part is kept as 6a and the apply/check part as the corrected 6b that was re-sent.
# The save of the live session is not included: this script never saves a .blend file and
# does not export.
#
# Run:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup ^
#       --python-exit-code 1 --python tools/blender/build_cover_wall.py

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

m_brick = make_material("M_Brick", "#8B4A3A")
m_dark = make_material("M_BrickDark", "#6E3B2E")
for m in (m_brick, m_dark):
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    print(m.name, [round(v, 4) for v in bsdf.inputs["Base Color"].default_value])

# --- Step 3: cover_wall_main, 4.0 x 1.0 x 1.5 m, underside centre at the world origin. -----
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

main = make_box("cover_wall_main", (4.0, 1.0, 1.5), (0.0, 0.0, 0.0),
                bpy.data.materials["M_Brick"])
print(main.name, "faces:", len(main.data.polygons), "verts:", len(main.data.vertices))

# --- Step 4: cover_wall_top_A, 1.6 x 1.0 x 0.3 m, x -2.0..-0.4, z 1.5..1.8 (highest point).
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

top_a = make_box("cover_wall_top_A", (1.6, 1.0, 0.3), (-1.2, 0.0, 1.5),
                 bpy.data.materials["M_BrickDark"])
print(top_a.name, "faces:", len(top_a.data.polygons), "verts:", len(top_a.data.vertices))

# --- Step 5: cover_wall_top_B, 1.0 x 0.8 x 0.15 m, x 0.4..1.4, y -0.4..0.4 (0.1 m in from
# the front face), z 1.5..1.65. --------------------------------------------------------------
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

top_b = make_box("cover_wall_top_B", (1.0, 0.8, 0.15), (0.9, 0.0, 1.5),
                 bpy.data.materials["M_BrickDark"])
print(top_b.name, "faces:", len(top_b.data.polygons), "verts:", len(top_b.data.vertices))

# --- Step 6a: join the three cubes into one mesh object 'cover_wall' (two material slots,
# origin at the centre of the underside = world origin). -----------------------------------
import bpy, bmesh

parts = [bpy.data.objects[n] for n in ("cover_wall_main", "cover_wall_top_A", "cover_wall_top_B")]
mats = [bpy.data.materials["M_Brick"], bpy.data.materials["M_BrickDark"]]

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

me = bpy.data.meshes.new("cover_wall")
bm.to_mesh(me)
bm.free()
for m in mats:
    me.materials.append(m)

for ob in parts:
    old = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(old)

wall = bpy.data.objects.new("cover_wall", me)
bpy.context.scene.collection.objects.link(wall)
wall.location = (0.0, 0.0, 0.0)

# --- Step 6b: apply rotation and scale on cover_wall, then check against CHANGE-BRIEF.md. --
import bpy

view_layer = bpy.context.view_layer
view_layer.update()
wall = bpy.data.objects["cover_wall"]
me = wall.data
for ob in bpy.context.scene.objects:
    ob.select_set(False)
wall.select_set(True)
view_layer.objects.active = wall
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
zs = [v.co.z for v in me.vertices]
size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
slots = [s.material.name for s in wall.material_slots]
errors = []
if any(abs(a - b) > 1e-4 for a, b in zip(size, (4.0, 1.0, 1.8))):
    errors.append(f"size {size}")
if abs(min(zs)) > 1e-4:
    errors.append(f"lowest z {min(zs)}")
if abs((max(xs) + min(xs)) / 2) > 1e-4 or abs((max(ys) + min(ys)) / 2) > 1e-4:
    errors.append("origin not at underside centre")
if tuple(wall.location) != (0.0, 0.0, 0.0):
    errors.append(f"location {tuple(wall.location)}")
if tuple(wall.rotation_euler) != (0.0, 0.0, 0.0) or tuple(wall.scale) != (1.0, 1.0, 1.0):
    errors.append("rotation/scale not applied")
if tris > 60:
    errors.append(f"{tris} triangles > 60")
if len(wall.modifiers):
    errors.append("modifiers present")
if slots != ["M_Brick", "M_BrickDark"]:
    errors.append(f"slots {slots}")
mesh_objects = [o.name for o in bpy.data.objects if o.type == "MESH"]
if mesh_objects != ["cover_wall"]:
    errors.append(f"mesh objects {mesh_objects}")

print("size:", tuple(round(s, 4) for s in size), "lowest z:", round(min(zs), 4))
print("triangles:", tris, "faces:", len(me.polygons), "verts:", len(me.vertices))
print("slots:", slots, "faces per slot:",
      [sum(1 for p in me.polygons if p.material_index == i) for i in range(len(slots))])
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])
if errors:
    raise RuntimeError("cover_wall checks failed: " + "; ".join(errors))
print("cover_wall checks passed")

# --- Step 7: Hand edit made by the student in Edit Mode (G X 0.6), reproduced here so the
# script matches the saved .blend. Block B (x 0.4..1.4) moves +0.6 m in X to x 1.0..2.0,
# flush with the right end. Its vertices are the ones with z 1.5..1.65 and |y| = 0.4; the z
# band alone would also catch the main box's top and block A's bottom (both at z 1.5, |y| 0.5).
# Note: the saved .blend measures block B at x 0.9993..1.9993 (moved +0.5993 m, 0.7 mm short
# of the intended 0.6); this step applies the exact 0.6. Then re-run the step 6b checks. ------
import bpy

wall = bpy.data.objects["cover_wall"]
me = wall.data
block_b = [v for v in me.vertices
           if 1.5 - 1e-4 <= v.co.z <= 1.65 + 1e-4 and abs(abs(v.co.y) - 0.4) < 1e-4]
if len(block_b) != 8:
    raise RuntimeError(f"expected 8 block B vertices, found {len(block_b)}")
for v in block_b:
    v.co.x += 0.6
me.update()

xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
zs = [v.co.z for v in me.vertices]
size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
slots = [s.material.name for s in wall.material_slots]
bx = [v.co.x for v in block_b]
errors = []
if any(abs(a - b) > 1e-4 for a, b in zip(size, (4.0, 1.0, 1.8))):
    errors.append(f"size {size}")
if abs(min(zs)) > 1e-4:
    errors.append(f"lowest z {min(zs)}")
if abs((max(xs) + min(xs)) / 2) > 1e-4 or abs((max(ys) + min(ys)) / 2) > 1e-4:
    errors.append("origin not at underside centre")
if tuple(wall.location) != (0.0, 0.0, 0.0):
    errors.append(f"location {tuple(wall.location)}")
if tuple(wall.rotation_euler) != (0.0, 0.0, 0.0) or tuple(wall.scale) != (1.0, 1.0, 1.0):
    errors.append("rotation/scale not applied")
if tris > 60:
    errors.append(f"{tris} triangles > 60")
if len(wall.modifiers):
    errors.append("modifiers present")
if slots != ["M_Brick", "M_BrickDark"]:
    errors.append(f"slots {slots}")
mesh_objects = [o.name for o in bpy.data.objects if o.type == "MESH"]
if mesh_objects != ["cover_wall"]:
    errors.append(f"mesh objects {mesh_objects}")
if abs(min(bx) - 1.0) > 1e-4 or abs(max(bx) - 2.0) > 1e-4:
    errors.append(f"block B x {min(bx)}..{max(bx)}, expected 1.0..2.0")

print("block B x:", round(min(bx), 4), "..", round(max(bx), 4))
print("size:", tuple(round(s, 4) for s in size), "lowest z:", round(min(zs), 4))
print("triangles:", tris, "faces:", len(me.polygons), "verts:", len(me.vertices))
print("slots:", slots, "faces per slot:",
      [sum(1 for p in me.polygons if p.material_index == i) for i in range(len(slots))])
print("objects:", [o.name for o in bpy.data.objects], "meshes:", [m.name for m in bpy.data.meshes])
if errors:
    raise RuntimeError("cover_wall checks after hand edit failed: " + "; ".join(errors))
print("cover_wall checks after hand edit passed")
