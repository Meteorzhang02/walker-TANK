"""Burn the provenance label onto the running-scene capture and cut it to B07's measured length (film tooling).
Frames are taken in order from frame 30 of capture/room-run.mp4 (no hold, no retiming).
Run: python scripts/make_b07.py
"""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
bold = ImageFont.truetype(str(FONTS / "Lato/static/Lato-Bold.ttf"), 64)
reg = ImageFont.truetype(str(FONTS / "Inter/static/Inter_28pt-Regular.ttf"), 46)
serif = ImageFont.truetype(str(FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf"), 60)
im = Image.new("RGBA", (3840, 2160), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
t1 = "RUNNING GODOT SCENE · res://scenes/asset_room_3d.tscn"
w = d.textlength(t1, font=bold)
d.rounded_rectangle([200, 110, 200 + w + 80, 230], radius=18, fill=(48, 61, 52, 235))
d.text((240, 132), t1, font=bold, fill=(255, 253, 248, 255))
t2 = "Godot 4.7.2 Movie Maker capture, isolated copy of commit 9baa12c · fixed camera, the scene has no motion"
w2 = d.textlength(t2, font=reg)
d.rounded_rectangle([200, 1930, 200 + w2 + 60, 2030], radius=14, fill=(48, 61, 52, 220))
d.text((230, 1950), t2, font=reg, fill=(255, 253, 248, 255))
d.text((3840 - 200 - d.textlength("@NikBearBrown", font=serif), 1945), "@NikBearBrown", font=serif, fill=(255, 253, 248, 200))
im.save(REEL / "capture/b07-label.png")
sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
frames = next(b for b in sheet["beats"] if b["beat_id"] == "B07")["audio_pad"]["frames"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(REEL / "capture/room-run.mp4"), "-i", str(REEL / "capture/b07-label.png"),
                "-filter_complex", f"[0:v]trim=start_frame=30:end_frame={30 + frames},setpts=PTS-STARTPTS[v];[v][1:v]overlay=0:0,format=yuv420p",
                "-an", "-r", "30", "-c:v", "libx264", "-crf", "12", "-preset", "slow", str(REEL / "media/B07.mp4")], check=True)
print("B07 frames", frames)
