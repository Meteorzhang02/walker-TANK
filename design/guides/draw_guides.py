"""Render img2img guide images for YunqiZ: hull-only and turret-only, 5 directions.
Code-drawn by Claude from the box model in draw_sketches.py (not generative-model output)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "character"))
import draw_sketches as D
SIZE=1024; S=600; BG="#FFFFFF"
DIRS=[("up",-90),("up-right",-45),("right",0),("down-right",45),("down",90)]
def render_parts(parts, ang, cx, cy, order_by_depth=True, skip_white_top=True):
    polys=[]
    for p in parts:
        b=p["b"]; c=D.rot(((b[0]+b[1])/2,(b[2]+b[3])/2,(b[4]+b[5])/2),ang)
        face_polys=[]
        for nrm,pts in D.faces(b):
            if skip_white_top and p["c"]==D.WHITE and nrm==(0,0,1): continue
            nr=D.rot(nrm,ang)
            if sum(nr[i]*D.V[i] for i in range(3))<=1e-6: continue
            rp=[D.rot(q,ang) for q in pts]
            lam=max(0,sum(nr[i]*D.L[i] for i in range(3)))
            col=D.shade(p["c"],0.55+0.6*lam)
            pts2=" ".join("%.1f,%.1f"%D.proj(q,S,cx,cy) for q in rp)
            face_polys.append(f'<polygon points="{pts2}" fill="{col}" stroke="#141515" stroke-width="3" stroke-linejoin="round"/>')
        polys.append((D.depth(c),p,face_polys))
    return polys
def hull_svg(yaw):
    a=math.radians(yaw); out=[]
    # anchor: hull origin (0,0,0) at image centre
    cx=cy=SIZE/2
    hc=D.depth(D.rot((0,0,0.15),a))
    att=[(D.depth(D.rot(((p["b"][0]+p["b"][1])/2,0,0.15),a)),p) for p in D.ATTACH]
    for d0,p in att:
        if d0<hc: out+=render_parts([p],a,cx,cy)[0][2]
    for p in D.tank_parts(): out+=render_parts([p],a,cx,cy)[0][2]
    for d0,p in att:
        if d0>=hc: out+=render_parts([p],a,cx,cy)[0][2]
    return out
PIVOT_Z=0.365
def turret_svg(yaw):
    a=math.radians(yaw); out=[]
    # anchor: turret pivot (0,0,PIVOT_Z) at image centre
    cx=SIZE/2; cy=SIZE/2+PIVOT_Z*math.cos(D.E)*S
    rp=render_parts(D.TURRET,a,cx,cy)
    body=[r for r in rp if r[1]["c"]==D.OLIVE][0]; band=[r for r in rp if r[1]["c"]==D.WHITE][0]; barrel=[r for r in rp if r[1]["c"]==D.DARK][0]
    order=[barrel,body,band] if barrel[0]<body[0] else [body,band,barrel]
    for r in order: out+=r[2]
    return out
def save(name,polys):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}"><rect width="100%" height="100%" fill="{BG}"/>{"".join(polys)}</svg>'
    open(name,"w").write(s)
import os; os.makedirs("guides",exist_ok=True)
for n,y in DIRS:
    save(f"guides/guide_hull_{n}.svg",hull_svg(y))
    save(f"guides/guide_turret_{n}.svg",turret_svg(y))
# in-game turret offset relative to hull origin, in pixels at guide scale
print("turret pivot offset from hull origin (px at guide scale): dx=0, dy=%.1f"%(-PIVOT_Z*math.cos(D.E)*S))
