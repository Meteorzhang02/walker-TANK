extends SceneTree
## Assignment 6 price measurement. Written by Claude (chat), run by me.
## Phases: an empty control, then previews/price_scene.tscn in mode 0, 1, 2, 3 and 0 again.
## Modes are switched with real key events (the price scene's own 0-3 keys).
## Per frame it records process and physics time (Performance monitors, CPU) and the
## viewport's measured render time on the CPU and the GPU (RenderingServer: the same
## numbers the Visual Profiler shows). Per phase it prints median, mean and p95 in ms.
## Medians, because single spike frames made the means unusable (cost_particles.gd).
##   windowed: "$GUI" --path . --script res://tests/price_measure.gd
##   headless: bash scripts/run-test.sh price_measure.gd realtime 300  (no GPU work runs there)

const WARM := 180
const SAMPLE := 720
const SCENE := "res://previews/price_scene.tscn"
const PHASES := [
    ["control_empty", -1],
    ["mode0_off", KEY_0],
    ["mode1_A_peak", KEY_1],
    ["mode2_B_peak", KEY_2],
    ["mode3_both", KEY_3],
    ["mode0_off_again", KEY_0],
]

var _medians := {}


func _initialize() -> void:
    _run()


func _run() -> void:
    var rid := root.get_viewport_rid()
    RenderingServer.viewport_set_measure_render_time(rid, true)
    print("PRICE cpu: %s" % OS.get_processor_name())
    print("PRICE gpu: %s / %s" % [RenderingServer.get_video_adapter_vendor(), RenderingServer.get_video_adapter_name()])
    print("PRICE display server: %s" % DisplayServer.get_name())
    print("PRICE warm %d frames, sample %d frames per phase" % [WARM, SAMPLE])
    var scene: Node = null
    for ph in PHASES:
        var phase_name: String = ph[0]
        var key: int = ph[1]
        if key >= 0:
            if scene == null:
                scene = load(SCENE).instantiate()
                root.add_child(scene)
                await _frames(30)
            await _press(key)
            print("PRICE %s label: %s" % [phase_name, _mode_label(scene)])
        await _frames(WARM)
        var process_ms: Array = []
        var physics_ms: Array = []
        var cpu_ms: Array = []
        var gpu_ms: Array = []
        for i in SAMPLE:
            await process_frame
            process_ms.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0)
            physics_ms.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0)
            cpu_ms.append(RenderingServer.viewport_get_measured_render_time_cpu(rid))
            gpu_ms.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
        _medians[phase_name] = {
            "process": _median(process_ms), "physics": _median(physics_ms),
            "render_cpu": _median(cpu_ms), "render_gpu": _median(gpu_ms),
        }
        print("PRICE %s | process %s | physics %s | render_cpu %s | render_gpu %s | fps %.0f" % [
            phase_name, _stats(process_ms), _stats(physics_ms), _stats(cpu_ms), _stats(gpu_ms),
            Engine.get_frames_per_second()])
    var pairs := [
        ["mode0_off", "control_empty"], ["mode1_A_peak", "mode0_off"],
        ["mode2_B_peak", "mode0_off"], ["mode3_both", "mode0_off"],
        ["mode0_off_again", "mode0_off"],
    ]
    for pair in pairs:
        var a: Dictionary = _medians[pair[0]]
        var b: Dictionary = _medians[pair[1]]
        print("PRICE diff %s - %s (medians) | process %+.4f | physics %+.4f | render_cpu %+.4f | render_gpu %+.4f" % [
            pair[0], pair[1], a["process"] - b["process"], a["physics"] - b["physics"],
            a["render_cpu"] - b["render_cpu"], a["render_gpu"] - b["render_gpu"]])
    quit(0)


func _frames(n: int) -> void:
    for i in n:
        await process_frame


func _press(code: int) -> void:
    var down := InputEventKey.new()
    down.keycode = code as Key
    down.physical_keycode = code as Key
    down.pressed = true
    Input.parse_input_event(down)
    await _frames(3)
    var up := InputEventKey.new()
    up.keycode = code as Key
    up.physical_keycode = code as Key
    up.pressed = false
    Input.parse_input_event(up)
    await _frames(3)


func _mode_label(n: Node) -> String:
    for c in n.find_children("*", "Label", true, false):
        var t: String = (c as Label).text
        if t.begins_with("Price mode"):
            return t.split("\n")[0]
    return "(no mode label found)"


func _sorted(a: Array) -> Array:
    var b := a.duplicate()
    b.sort()
    return b


func _median(a: Array) -> float:
    var b := _sorted(a)
    return b[int(b.size() / 2.0)]


func _stats(a: Array) -> String:
    var b := _sorted(a)
    var mean := 0.0
    for v in b:
        mean += v
    mean /= b.size()
    return "median %.4f mean %.4f p95 %.4f" % [b[int(b.size() / 2.0)], mean, b[int(b.size() * 0.95)]]
