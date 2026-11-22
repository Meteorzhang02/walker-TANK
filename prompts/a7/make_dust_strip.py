# A7 (mine, with Claude chat): frames 70-75 (driving right) of a capture side by side, labelled.
import sys
from PIL import Image, ImageDraw
src, out, tag = sys.argv[1], sys.argv[2], sys.argv[3]
frames = [Image.open(f"{src}/shoot{70 + k:08d}.png").convert("RGB") for k in range(6)]
w, h = frames[0].size
cw, ch = w // 2, h // 2
tiles = [f.crop((w // 2 - cw // 2, h // 2 - ch // 2, w // 2 + cw // 2, h // 2 + ch // 2)) for f in frames]
strip = Image.new("RGB", (cw * 6, ch + 28), "white")
d = ImageDraw.Draw(strip)
for k, t in enumerate(tiles):
    strip.paste(t, (k * cw, 28))
    d.text((k * cw + 6, 6), f"{tag} frame {70 + k}", fill="black")
strip.save(out)
print("strip:", out)
