"""Resize the finished 1024 px sprites to in-game textures (written by Claude).
In-game display scale is 0.0864 of the 1024 px source (hull about 64 px across). Textures are saved
at twice that (0.1728) and drawn at scale 0.5, so they stay sharp when the window is scaled up.
The ground tile is saved at 192 px."""
import os
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=0.1728
def rs(src,dst,scale=None,size=None):
    im=Image.open(os.path.join(ROOT,src))
    if size: out=im.resize(size,Image.LANCZOS)
    else: out=im.resize((round(im.width*scale),round(im.height*scale)),Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.join(ROOT,dst)),exist_ok=True); out.save(os.path.join(ROOT,dst))
for d in ["right","down_right","down","up","up_right"]:
    rs(f"assets/sprites/yunqiz/hull/CHAR-hull_{d}.png",f"assets/game/yunqiz/hull_{d}.png",S)
    rs(f"assets/sprites/yunqiz/turret/CHAR-turret_{d}.png",f"assets/game/yunqiz/turret_{d}.png",S)
for n in ["intact","cracked","broken"]:
    rs(f"assets/sprites/env/ENV-cover_{n}.png",f"assets/game/env/cover_{n}.png",S)
rs("assets/sprites/env/ENV-ground_tile.png","assets/game/env/ground_tile.png",size=(192,192))
