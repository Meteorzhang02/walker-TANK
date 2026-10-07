"""Make a generated texture tile seamlessly (written by Claude). Edit: blend the image with a copy
shifted by half its size in both directions; the shifted copy is used near the edges (where it is
continuous across the wrap) and the original in the middle, with a smooth mask between them."""
import sys, numpy as np
from PIL import Image
def tile(src,dst,margin=0.22):
    a=np.asarray(Image.open(src).convert("RGB")).astype(np.float32); h,w,_=a.shape
    r=np.roll(a,(h//2,w//2),axis=(0,1))
    def ramp(n):
        t=np.minimum(np.arange(n),np.arange(n)[::-1])/(n*margin); t=np.clip(t,0,1); return t*t*(3-2*t)
    m=np.outer(ramp(h),ramp(w))[...,None]
    out=a*m+r*(1-m)
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(dst)
if __name__=="__main__": tile(sys.argv[1],sys.argv[2])
