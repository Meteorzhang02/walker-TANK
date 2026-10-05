"""YunqiZ sprite post-processing (written by Claude). Recorded edits, in order:
1. Turrets only: paint the off-white identification stripe (#E8E6DF) where the v3 guide puts it,
   keeping the generated shading underneath (stripe position from stripe_mask_<dir>.png).
2. Cut the sprite off its white background (cutout_hull.cutout).
3. Hull and turret: match the olive paint to the character-sheet main color #4B5320 with a
   per-channel gain, applied only to olive (green-dominant) pixels so grey steel is untouched."""
import os, sys, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout_hull import cutout
STRIPE=np.array([0xE8,0xE6,0xDF],np.float32)
TARGET=np.array([0x4B,0x53,0x20],np.float32)
def stripe_mask(path):
    a=np.asarray(Image.open(path).convert("RGB")).astype(int)
    m=((a[...,0]>200)&(a[...,1]<60)&(a[...,2]<60)).astype(np.uint8)*255
    return np.asarray(Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)/255
def paint_stripe(src, mask_png, dst):
    a=np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    m=stripe_mask(mask_png)
    L=a.mean(axis=2); med=np.median(L[m>0.5]) if (m>0.5).any() else 128
    shade=np.clip(0.82+0.18*(L/max(med,1)),0.7,1.05)[...,None]
    painted=STRIPE*shade
    out=a*(1-m[...,None])+painted*m[...,None]
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(dst)
def olive_weight(rgb):
    return np.clip((rgb[...,1]-rgb[...,2]-12)/25,0,1)
def olive_mean(rgba):
    rgb=rgba[...,:3].astype(np.float32); a=rgba[...,3]>200; w=olive_weight(rgb)*a
    return (rgb*w[...,None]).sum(axis=(0,1))/max(w.sum(),1)
def color_match(path):
    im=np.asarray(Image.open(path).convert("RGBA")).copy()
    rgb=im[...,:3].astype(np.float32); before=olive_mean(im)
    gain=np.clip(TARGET/np.maximum(before,1),0.75,1.3)
    w=olive_weight(rgb)[...,None]
    rgb=rgb*(1-w)+np.clip(rgb*gain,0,255)*w
    im[...,:3]=np.clip(rgb,0,255).astype(np.uint8)
    Image.fromarray(im,"RGBA").save(path)
    return before, olive_mean(im), gain
