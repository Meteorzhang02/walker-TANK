"""Add subtle grain and weathering to rendered guide PNGs (numpy/PIL, fixed seed)."""
import numpy as np, glob, sys
from PIL import Image, ImageFilter
rng=np.random.default_rng(7)
def tex(path):
    im=np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    mask=(im.min(axis=2)<250).astype(np.float32)
    m=Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
    mask=np.asarray(m).astype(np.float32)/255
    h,w=mask.shape
    grain=rng.normal(0,7,(h,w)).astype(np.float32)
    grain=np.asarray(Image.fromarray(np.clip(grain+128,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)-128
    low=rng.normal(0,1,(h//32+1,w//32+1)).astype(np.float32)
    low=np.asarray(Image.fromarray(((low-low.min())/(np.ptp(low))*255).astype(np.uint8)).resize((w,h),Image.BICUBIC)).astype(np.float32)/255
    grime=np.clip((low-0.55)*2.2,0,1)*0.22      # darker brownish patches
    out=im.copy()
    out=out*(1-grime[...,None]) + np.array([70,58,40])*grime[...,None]
    out=out+grain[...,None]*1.0
    out=im*(1-mask[...,None])+out*mask[...,None]
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(path)
for f in sorted(glob.glob(sys.argv[1]+"/*.png")):
    if "preview" in f: continue
    tex(f)
