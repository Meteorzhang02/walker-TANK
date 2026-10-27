shader_type canvas_item;

uniform float hit_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 0.0, 0.0, 1.0);
uniform float flash_strength : hint_range(0.0, 1.0) = 0.6;

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, hit_amount * flash_strength);
}