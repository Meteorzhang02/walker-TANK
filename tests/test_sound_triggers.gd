extends SceneTree
## Automated check that each sound plays once per event and that sound never decides game state.
## Run from the project folder (open the project in the editor once first so assets are imported):
##   godot --headless --path . -s res://tests/test_sound_triggers.gd

var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if not ok:
		failures += 1


func _run() -> void:
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await physics_frame
	var a = main.audio
	var p = main.player
	var ShellScript = load("res://scripts/shell.gd")

	# 1. Rapid fire: ten presses in one frame give one shell and one sound.
	var f0: int = a.count("fire")
	var shots := 0
	for i in 10:
		if p.try_fire():
			shots += 1
	_check("10 fire presses in one frame -> 1 shell, 1 fire sound", shots == 1 and a.count("fire") - f0 == 1)
	p.reload_left = 0.0
	p.try_fire()
	_check("fire again after reload -> 2nd fire sound", a.count("fire") - f0 == 2)

	# 2. One shell touching the same cover twice gives one hit and one sound.
	var covers: Array = main.actors.get_children().filter(func(n): return n.has_method("take_hit"))
	var cover = covers[0]
	var c0: int = a.count("cover_hit")
	var s1 = ShellScript.new()
	s1.world = main
	s1.shooter = p
	main.fx_layer.add_child(s1)
	s1._on_body_entered(cover)
	s1._on_body_entered(cover)
	_check("one shell touching cover twice -> 1 cover-hit sound", a.count("cover_hit") - c0 == 1 and cover.hits == 1)

	# 3. Two shells hitting the same cover in the same frame: two hits, two sounds, stage advances.
	var s2 = ShellScript.new()
	var s3 = ShellScript.new()
	for s in [s2, s3]:
		s.world = main
		s.shooter = p
		main.fx_layer.add_child(s)
	s2._on_body_entered(cover)
	s3._on_body_entered(cover)
	_check("two shells in one frame -> 2 more cover-hit sounds, cover cracked", a.count("cover_hit") - c0 == 3 and cover.stage == 1)

	# 4. Two hits inside the 0.3 s invulnerability window -> one hit sound, damage once.
	p.invuln_left = 0.0
	var h0: int = a.count("player_hit")
	var hp: int = p.health
	p.take_damage(10)
	p.take_damage(10)
	_check("two hits within 0.3 s -> 1 hit sound, damage applied once", a.count("player_hit") - h0 == 1 and p.health == hp - 10)

	# 5. Fatal hit plays the explosion (not the hit sound); dying twice explodes once.
	p.invuln_left = 0.0
	p.health = 10
	h0 = a.count("player_hit")
	var e0: int = a.count("explode")
	p.take_damage(25)
	p.die()
	_check("fatal hit -> 1 explosion, 0 hit sounds, dead", a.count("explode") - e0 == 1 and a.count("player_hit") - h0 == 0 and p.is_dead)

	# 6. Victory sound plays once even if the last-enemy event fires twice.
	main.remaining = 1
	var v0: int = a.count("victory")
	main._on_enemy_destroyed(null)
	main._on_enemy_destroyed(null)
	_check("last enemy destroyed twice -> 1 victory sound", a.count("victory") - v0 == 1 and main.level_won)

	# 7. Sound does not decide game state: with SFX muted, damage and cover breaking still happen.
	a.set_bus_muted("SFX", true)
	var e = main.enemies[0]
	e.invuln_left = 0.0
	var ehp: int = e.health
	e.take_damage(25)
	var cover2 = covers[1]
	for i in 4:
		cover2.take_hit()
	_check("SFX muted -> enemy still damaged, cover still breaks", e.health == ehp - 25 and cover2.stage == 2)
	a.set_bus_muted("SFX", false)

	print("RESULT: %d failed" % failures)
	main.queue_free()
	await process_frame
	quit(1 if failures > 0 else 0)
