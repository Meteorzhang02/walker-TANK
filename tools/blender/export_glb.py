# Exports the open .blend file as binary glTF (.glb) for Godot (CHANGE-BRIEF.md, common rules).
#
# Options set: GLB, +Y Up on, materials exported; cameras, lights and animation off. Every
# other exporter option stays at Blender's default. The .blend file is never saved, and the
# script runs in its own background process, so a live Blender session is not touched.
#
# Run (one asset per call; the .blend path comes before --python, the output after --):
#   "D:\blender\blender.exe" -b --factory-startup --python-exit-code 1 ^
#       design/blender/cover_wall.blend --python tools/blender/export_glb.py ^
#       -- assets/models/cover_wall.glb
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) != 1 or not argv[0].lower().endswith(".glb"):
    raise SystemExit("usage: ... --python export_glb.py -- <output>.glb")
out_path = os.path.abspath(argv[0])
os.makedirs(os.path.dirname(out_path), exist_ok=True)

options = {
    "export_format": "GLB",
    "export_yup": True,
    "export_materials": "EXPORT",
    "export_cameras": False,
    "export_lights": False,
    "export_animations": False,
}
# Fail loudly if this Blender's exporter does not have one of these option names.
props = bpy.ops.export_scene.gltf.get_rna_type().properties
missing = [k for k in options if k not in props]
if missing:
    raise SystemExit(f"glTF exporter has no option(s): {missing}")

print("source:", bpy.data.filepath)
for ob in bpy.data.objects:
    line = f"  object {ob.name!r} type={ob.type}"
    if ob.type == "MESH":
        me = ob.data
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        line += (f" tris={tris} mats={[m.name for m in me.materials if m]}"
                 f" loc={tuple(round(v, 4) for v in ob.location)}"
                 f" rot={tuple(round(v, 4) for v in ob.rotation_euler)}"
                 f" scale={tuple(round(v, 4) for v in ob.scale)}")
    print(line)

result = bpy.ops.export_scene.gltf(filepath=out_path, **options)
if result != {"FINISHED"} or not os.path.isfile(out_path):
    raise SystemExit(f"export failed: {result}")
print("exported:", out_path, os.path.getsize(out_path), "bytes")
