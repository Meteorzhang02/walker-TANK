"""Cut generated hull sprites off their white background and build check sheets.
Written by Claude. Steps per image: flood-fill near-white from the border as background,
keep the largest connected foreground component (drops VAE edge specks), feather the edge
by 1 px, and remove the light fringe left by the white background."""
import sys, os, numpy as np
from collections import deque
from PIL import Image, ImageFilter
from scipy import ndimage
TOL=18
def fg_mask(a):
    h,w,_=a.shape
    near=(255-a.astype(int)).max(axis=2)<TOL
    lab,n=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    fg=~bg
    fg=ndimage.binary_opening(fg,iterations=2)
    # keep every sizeable part (the blade can be separate from the hull), drop specks
    lab,n=ndimage.label(fg)
    if n>1:
        sizes=ndimage.sum(fg,lab,range(1,n+1))
        keep=[i+1 for i,s in enumerate(sizes) if s>=2000]
        fg=np.isin(lab,keep)
    # white background trapped between parts (e.g. under the blade): pure white, enclosed
    pure=(255-a.astype(int)).max(axis=2)<8
    lab2,n2=ndimage.label(pure&fg)
    if n2:
        sizes=ndimage.sum(pure&fg,lab2,range(1,n2+1))
        holes=[i+1 for i,s in enumerate(sizes) if s>=40]
        fg=fg&~np.isin(lab2,holes)
    return fg
def cutout(src,dst):
    a=np.asarray(Image.open(src).convert("RGB"))
    m=fg_mask(a)
    alpha=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    al=np.asarray(alpha).astype(np.float32)/255
    rgb=a.astype(np.float32)
    # un-premultiply against white on soft edge pixels to remove white halo
    edge=(al>0.02)&(al<0.98)
    rgb[edge]=np.clip((rgb[edge]-255*(1-al[edge,None]))/np.maximum(al[edge,None],0.05),0,255)
    out=np.dstack([rgb,al*255]).astype(np.uint8)
    Image.fromarray(out,"RGBA").save(dst)
    return m
if __name__=="__main__":
    for src in sys.argv[1:-1]:
        cutout(src, os.path.join(sys.argv[-1], os.path.basename(src).replace("_00001_","")))
