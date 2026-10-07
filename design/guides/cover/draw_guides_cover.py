"""img2img guides for ENV-cover (brick wall block) in three stages: intact, cracked, broken.
Same oblique view and scale (S=600 px per unit) as the YunqiZ guides, so cover and tank match in size.
Code-drawn by Claude (not generative-model output)."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2"))
import draw_guides_v2 as G
D=G.D
BRICK="#7a5c4a"; MORTAR="#4a3a30"
W_,DEP,H_=1.4,0.4,0.35
def brick_lines(face, x0,x1,y0,y1,z0,z1, ang,cx,cy, rows=5, seed=0):
    out=[]; rh=(z1-z0)/rows; bw=0.18
    for r in range(rows+1):
        z=z0+r*rh
        if face=="front": out.append(G.line3((x0,y1+0.001,z),(x1,y1+0.001,z),ang,cx,cy,MORTAR,3))
    for r in range(rows):
        z=z0+r*rh; off=(bw/2 if r%2 else 0)
        x=x0+off
        while x<x1:
            if face=="front": out.append(G.line3((x,y1+0.001,z),(x,y1+0.001,z+rh),ang,cx,cy,MORTAR,3))
            x+=bw
    return out
def top_lines(x0,x1,y0,y1,z,ang,cx,cy):
    out=[G.line3((x0,(y0+y1)/2,z+0.001),(x1,(y0+y1)/2,z+0.001),ang,cx,cy,MORTAR,3)]
    x=x0
    while x<x1: out.append(G.line3((x,y0,z+0.001),(x,y1,z+0.001),ang,cx,cy,MORTAR,3)); x+=0.18
    return out
def block(x0,x1,y0,y1,z0,z1,ang,cx,cy,color=BRICK,bricks=True):
    p={"b":(x0,x1,y0,y1,z0,z1),"c":color}; out=[]
    for nrm,pts in D.faces(p["b"]):
        vis,nr=G.visible(nrm,ang)
        if not vis: continue
        out.append(G.poly(pts,ang,cx,cy,color,G.light(nr)))
        if bricks and nrm==(0,1,0): out+=brick_lines("front",x0,x1,y0,y1,z0,z1,ang,cx,cy,rows=max(1,round((z1-z0)/0.07)))
        if bricks and nrm==(0,0,1): out+=top_lines(x0,x1,y0,y1,z1,ang,cx,cy)
    return out
def crack(points,ang,cx,cy,w=5):
    p=[D.proj(D.rot(q,0),G.S,cx,cy) for q in points]
    return f'<polyline points="{" ".join("%.1f,%.1f"%q for q in p)}" fill="none" stroke="#1a1410" stroke-width="{w}" stroke-linejoin="round"/>'
def stage(n):
    cx=G.SIZE/2; cy=G.SIZE/2+0.12*G.S; out=[]
    x0,x1,y0,y1=-W_/2,W_/2,-DEP/2,DEP/2
    if n=="intact":
        out+=block(x0,x1,y0,y1,0,H_,0,cx,cy)
    elif n=="cracked":
        # notch: the right end has lost its top course of bricks
        out+=block(0.42,x1,y0,y1,0,0.25,0,cx,cy)
        out+=block(x0,0.42,y0,y1,0,H_,0,cx,cy)
        out.append(crack([(-0.35,y1+0.002,H_),(-0.28,y1+0.002,0.24),(-0.32,y1+0.002,0.15),(-0.24,y1+0.002,0.05)],0,cx,cy))
        out.append(crack([(0.10,y1+0.002,H_),(0.16,y1+0.002,0.22),(0.10,y1+0.002,0.12)],0,cx,cy))
        out.append(crack([(0.42,y1+0.002,0.25),(0.36,y1+0.002,0.16),(0.40,y1+0.002,0.06)],0,cx,cy,4))
    else:  # broken: low ragged remains plus rubble
        random.seed(4)
        segs=[(-0.70,-0.38,0.16),(-0.38,-0.05,0.10),(-0.05,0.30,0.19),(0.30,0.70,0.08)]
        rub=[]
        for i in range(26):
            x=random.uniform(-0.78,0.78); y=random.choice([random.uniform(y1+0.03,y1+0.25),random.uniform(y0-0.12,y0-0.03)]); s=random.uniform(0.04,0.09)
            rub.append((y,x,s))
        back=[r for r in sorted(rub) if r[0]<y0]; front=[r for r in sorted(rub) if r[0]>y1]
        for y,x,s in back:
            out+=block(x-s/2,x+s/2,y-s/3,y+s/3,0,s*0.55,0,cx,cy,color=random.choice([BRICK,"#8a6a56","#6a4e3e"]),bricks=False)
        for a,b,h in segs: out+=block(a,b,y0,y1,0,h,0,cx,cy)
        for y,x,s in front:
            out+=block(x-s/2,x+s/2,y-s/3,y+s/3,0,s*0.55,0,cx,cy,color=random.choice([BRICK,"#8a6a56","#6a4e3e"]),bricks=False)
    return out
if __name__=="__main__":
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    for n in ("intact","cracked","broken"): G.save(os.path.join(out,f"guide_cover_{n}.svg"),stage(n))
