"""Build media/B03.mp4 from the student's screen recording of play (film tooling).
Frames are taken in order from source frame 135 (4.5 s) of D:/CSYE7270/a5-evidence/play.mp4 for exactly B03's
measured frame count: no hold, no retiming, no crop; scaled only and placed on the cream page with a burned-in label.
The recording's own audio is not used (narration beat).
Run: python scripts/make_b03.py
"""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
SRC = Path(r"D:/CSYE7270/a5-evidence/play.mp4")
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
START = 135  # source frame (4.5 s at 30 fps): first hit at 6.65 s, second at 11.0 s
VW, VH, VX, VY = 2614, 1640, 613, 290  # 1294x812 scaled by 2.0197 (aspect kept)

serif = ImageFont.truetype(str(FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf"), 112)
bold = ImageFont.truetype(str(FONTS / "Lato/static/Lato-Bold.ttf"), 56)
reg = ImageFont.truetype(str(FONTS / "Inter/static/Inter_28pt-Regular.ttf"), 44)
small = ImageFont.truetype(str(FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf"), 56)

bg = Image.new("RGB", (3840, 2160), "#FAF9F5")
d = ImageDraw.Draw(bg)
d.text((211, 70), "Screen recording of my play", font=serif, fill="#3D3929")
lab = "SCREEN RECORDING OF MY PLAY · not a scripted capture"
w = d.textlength(lab, font=bold)
d.rounded_rectangle([3840 - 211 - w - 70, 100, 3840 - 211, 200], radius=14, fill="#303D34")
d.text((3840 - 211 - w - 35, 118), lab, font=bold, fill="#FFFDF8")
d.rectangle([VX - 4, VY - 4, VX + VW + 3, VY + VH + 3], outline="#CFC6B5", width=6)
prov = "a5-evidence/play.mp4 · the student's recording, 1294 × 812 at 30 fps · 4.5–14.7 s, frames in order, scaled only"
d.text((211, 1990), prov, font=reg, fill="#564739")
d.text((3840 - 211 - d.textlength("@NikBearBrown", font=small), 1975), "@NikBearBrown", font=small, fill="#3D3929")
(REEL / "capture").mkdir(exist_ok=True)
bg.save(REEL / "capture/b03-page.png")

sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
frames = next(b for b in sheet["beats"] if b["beat_id"] == "B03")["audio_pad"]["frames"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(REEL / "capture/b03-page.png"), "-i", str(SRC),
                "-filter_complex",
                f"[1:v]trim=start_frame={START}:end_frame={START + frames},setpts=PTS-STARTPTS,"
                f"scale={VW}:{VH}:flags=lanczos[v];[0:v][v]overlay={VX}:{VY}:shortest=1,format=yuv420p",
                "-an", "-r", "30", "-frames:v", str(frames), "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                "-threads", "4", str(REEL / "media/B03.mp4")], check=True)
print("B03 frames", frames, "source", START, "to", START + frames)
