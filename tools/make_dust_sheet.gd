# tools/make_dust_sheet.gd — writes the track_dust sprite sheet (A7).
# Run:  "$GODOT" --headless --path . --script res://tools/make_dust_sheet.gd
# Output: res://assets/game/fx/track_dust_sheet.png, 4 cells of 16x16 in one row.
# Each cell holds four puffs one life stage apart, so cell 3 -> cell 0 continues
# the emission instead of restarting it (the seam rule in CHANGE-BRIEF.md).
extends SceneTree

const OUT := "res://assets/game/fx/track_dust_sheet.png"
const CELL := 16
const FRAMES := 4
const DUST := Color(0.86, 0.80, 0.66)   # muddy brown, between ground and broken brick
# Where each puff is born inside the cell, and which way it drifts (cell px).
const BIRTH: Array[Vector2] = [Vector2(4, 12), Vector2(9, 13), Vector2(12, 11), Vector2(7, 10)]
const DRIFT := Vector2(0.5, -1.5)


func _init() -> void:
	var img := Image.create_empty(CELL * FRAMES, CELL, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for f in FRAMES:
		for x in CELL:
			for y in CELL:
				var a := 0.0
				for k in BIRTH.size():
					var life := float((f + k) % FRAMES) / FRAMES      # 0, .25, .5, .75
					var c := BIRTH[k] + DRIFT * life * 3.0
					var r := 1.5 + life * 3.5
					var d := Vector2(x + 0.5, y + 0.5).distance_to(c)
					if d < r:
						a = maxf(a, (1.0 - d / r) * 1.0 * (1.0 - life))
				if a > 0.0:
					img.set_pixel(f * CELL + x, y, Color(DUST.r, DUST.g, DUST.b, a))
	DirAccess.make_dir_recursive_absolute("res://assets/game/fx")
	var err := img.save_png(OUT)
	print("dust sheet: %s -> %s (%dx%d, %d cells)" % [OUT, error_string(err), img.get_width(), img.get_height(), FRAMES])
	quit(0 if err == OK else 1)
