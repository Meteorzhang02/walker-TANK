# A7 frame strip (mine, with Claude chat): frames N..N+5 of the shoot capture side by side, labelled.
import re, sys
from PIL import Image, ImageDraw
log, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(re.search(r"TRIGGER frame (\d+)", open(log, encoding="utf-8", errors="replace").read()).group(1))
labels = ["N startup", "N+1 active", "N+2 recovery", "N+3", "N+4", "N+5 end"]
frames = [Image.open(f"{src}/shoot{n + k:08d}.png").convert("RGB") for k in range(6)]
w, h = frames[0].size
cw, ch = w // 2, h // 2
cx, cy = w // 2, h // 2
tiles = [f.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)) for f in frames]
strip = Image.new("RGB", (cw * 6, ch + 28), "white")
d = ImageDraw.Draw(strip)
for k, t in enumerate(tiles):
    strip.paste(t, (k * cw, 28))
    d.text((k * cw + 6, 6), f"{labels[k]} (frame {n + k})", fill="black")
strip.save(out)
print("strip:", out, "N =", n)
