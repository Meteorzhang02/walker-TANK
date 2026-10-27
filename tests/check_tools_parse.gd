extends SceneTree
## A5 Use It capture tools: checks that each tool script parses (loads as a GDScript that
## can_instantiate() and extends SceneTree). It never runs them: they need a windowed run.
##   bash scripts/run-test.sh check_tools_parse.gd 60

const TOOLS := [
	"res://tools/capture_hit_flash.gd",
	"res://tools/capture_hint.gd",
	"res://tools/capture_materials.gd",
]

var failures := 0
var passes := 0


func _initialize() -> void:
	for path in TOOLS:
		var s = load(path) if ResourceLoader.exists(path) else null
		_check("%s loads as a GDScript" % path, s is GDScript)
		if not (s is GDScript):
			continue
		var gd := s as GDScript
		_check("%s can_instantiate()" % path, gd.can_instantiate())
		_check("%s extends SceneTree (base %s)" % [path, gd.get_instance_base_type()], gd.get_instance_base_type() == &"SceneTree")
	print("RESULT: %d passed, %d failed" % [passes, failures])
	quit(1 if failures > 0 else 0)


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if ok:
		passes += 1
	else:
		failures += 1
