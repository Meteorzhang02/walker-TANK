extends SceneTree
## tools/make_hint_png.gd — writes res://assets/hint/grey_3x1.png for the hint experiment
## (CHANGE-BRIEF.md section 4): a 3x1 RGB8 image, greys 64, 128, 192 from left to right.
## Run: <godot_console.exe> --headless --path . --script res://tools/make_hint_png.gd
## Then import it in the editor: Lossless, no mipmaps, Detect 3D Compress To = Disabled.

const OUT := "res://assets/hint/grey_3x1.png"
const GREYS := [64, 128, 192]


func _initialize() -> void:
	var err := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT.get_base_dir()))
	if err != OK:
		print("ERROR: could not create %s (%d)" % [OUT.get_base_dir(), err])
		quit(1)
		return
	var img := Image.create(GREYS.size(), 1, false, Image.FORMAT_RGB8)
	for x in GREYS.size():
		img.set_pixel(x, 0, Color8(GREYS[x], GREYS[x], GREYS[x]))
	err = img.save_png(ProjectSettings.globalize_path(OUT))
	if err != OK:
		print("ERROR: save_png failed (%d)" % err)
		quit(1)
		return
	# Read the file back and print what is actually stored.
	var back := Image.load_from_file(ProjectSettings.globalize_path(OUT))
	if back == null:
		print("ERROR: could not read back ", OUT)
		quit(1)
		return
	print("wrote %s  size %dx%d  format %d" % [OUT, back.get_width(), back.get_height(), back.get_format()])
	for x in back.get_width():
		var c := back.get_pixel(x, 0)
		print("  pixel %d: (%d, %d, %d)" % [x, c.r8, c.g8, c.b8])
	quit(0)
