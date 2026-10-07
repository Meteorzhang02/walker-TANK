"""Calm a busy ground texture so sprites read on top of it (written by Claude).
Edit: soften fine detail (Gaussian blur r=1.5), reduce contrast to 45% around the mean,
darken and pull toward a muddy brown (#4a3e33), then make it tile (make_tile.tile)."""
import sys, numpy as np, os
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_tile import tile
def calm(src,dst,contrast=0.45,target=(0x4a,0x3e,0x33),mix=0.35,blur=1.5):
    im=Image.open(src).convert("RGB").filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(im).astype(np.float32); mean=a.mean(axis=(0,1))
    a=mean+(a-mean)*contrast
    a=a/ a.mean(axis=(0,1)) * np.array(target,np.float32)
    a=a*(1-mix)+np.array(target,np.float32)*mix + (a-a.mean(axis=(0,1)))*mix
    tmp=dst.replace(".png","_untiled.png"); Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(tmp)
    tile(tmp,dst); os.remove(tmp)
if __name__=="__main__": calm(sys.argv[1],sys.argv[2])
