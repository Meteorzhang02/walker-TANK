"""Textured img2img guide images for YunqiZ (v2): hull-only and turret-only, 5 directions.
Code-drawn by Claude from the box model in draw_sketches.py (not generative-model output).
v2 removes black outlines and adds face gradients, grain/grime texture and structural
details (road wheels, deck panel lines, hatches, blade ribs) so img2img reads it as a real object."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "character"))
try:
    import draw_sketches as D
except ImportError:
    import draw as D
SIZE=1024; S=600; BG="#FFFFFF"
DIRS=[("up",-90),("up-right",-45),("right",0),("down-right",45),("down",90)]
gid=[0]; defs=[]
def grad_fill(color, k, pts2d):
    ys=[p[1] for p in pts2d]; y0,y1=min(ys),max(ys)
    if y1-y0<1: y1=y0+1
    gid[0]+=1; i=f"g{gid[0]}"
    c1=D.shade(color,k*1.12); c2=D.shade(color,k*0.82)
    defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="0" y1="{y0:.1f}" x2="0" y2="{y1:.1f}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    return f"url(#{i})"
def poly(pts3, ang, cx, cy, color, k, edge=True):
    p2=[D.proj(D.rot(q,ang),S,cx,cy) for q in pts3]
    s=" ".join("%.1f,%.1f"%p for p in p2)
    stroke=D.shade(color,k*1.35) if edge else "none"
    return f'<polygon points="{s}" fill="{grad_fill(color,k,p2)}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
def line3(a,b,ang,cx,cy,col,w=2):
    p=D.proj(D.rot(a,ang),S,cx,cy); q=D.proj(D.rot(b,ang),S,cx,cy)
    return f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
def visible(nrm,ang):
    nr=D.rot(nrm,ang); return sum(nr[i]*D.V[i] for i in range(3))>1e-6, nr
def light(nr): return 0.55+0.6*max(0,sum(nr[i]*D.L[i] for i in range(3)))
def circle3(c, r, plane, ang, cx, cy, color, k):
    pts=[]
    for i in range(20):
        t=2*math.pi*i/20
        if plane=="xz": pts.append((c[0]+r*math.cos(t), c[1], c[2]+r*math.sin(t)))
        else: pts.append((c[0]+r*math.cos(t), c[1]+r*math.sin(t), c[2]))
    return poly(pts,ang,cx,cy,color,k)
def part_svg(p, ang, cx, cy, details=None):
    out=[]
    for nrm,pts in D.faces(p["b"]):
        if p["c"]==D.WHITE and nrm==(0,0,1): continue
        vis,nr=visible(nrm,ang)
        if not vis: continue
        out.append(poly(pts,ang,cx,cy,p["c"],light(nr)))
        if details: out+=details(nrm,nr,ang,cx,cy)
    return out
# ---- details per part ----
def track_details(side):
    def f(nrm,nr,ang,cx,cy):
        out=[]
        if nrm==(0,side,0):
            y=0.31*side+0.002*side
            for x in (-0.38,-0.19,0.0,0.19,0.38):
                out.append(circle3((x,y,0.10),0.075,"xz",ang,cx,cy,"#3a3c3c",light(nr)))
                out.append(circle3((x,y+0.001*side,0.10),0.025,"xz",ang,cx,cy,"#6a6d6f",light(nr)))
        if nrm==(0,0,1):
            for x in [i*0.05-0.475 for i in range(20)]:
                out.append(line3((x,0.13*side,0.201),(x,0.31*side,0.201),ang,cx,cy,"#0c0c0c",2))
        return out
    return f
def deck_details(nrm,nr,ang,cx,cy):
    out=[]
    if nrm==(0,0,1):
        z=0.291; col="#2c3112"
        out.append(line3((-0.44,0.17,z),(0.44,0.17,z),ang,cx,cy,col))
        out.append(line3((-0.44,-0.17,z),(0.44,-0.17,z),ang,cx,cy,col))
        out.append(line3((-0.26,-0.30,z),(-0.26,0.30,z),ang,cx,cy,col))
        for x in (-0.42,-0.38,-0.34,-0.30):  # engine grille
            out.append(line3((x,-0.14,z),(x,0.14,z),ang,cx,cy,"#1f230c",3))
        out.append(circle3((0.33,0.22,z),0.045,"xy",ang,cx,cy,"#4B5320",light(nr)*0.9))  # driver hatch
        for x in (0.40,0.40):  # chipped edge marks
            pass
    return out
def blade_details(nrm,nr,ang,cx,cy):
    out=[]
    if nrm==(1,0,0):
        for y in [i*0.1-0.3 for i in range(7)]:
            out.append(line3((0.601,y,0.03),(0.601,y,0.19),ang,cx,cy,"#55585b",3))
        out.append(line3((0.601,-0.36,0.04),(0.601,0.36,0.04),ang,cx,cy,"#a9adb0",2))
    return out
def box_details(nrm,nr,ang,cx,cy):
    out=[]
    if nrm==(0,0,1):
        out.append(line3((-0.60,-0.20,0.311),(-0.49,-0.20,0.311),ang,cx,cy,"#20240b"))
        out.append(line3((-0.60,0.20,0.311),(-0.49,0.20,0.311),ang,cx,cy,"#20240b"))
    if nrm==(-1,0,0):
        out.append(line3((-0.621,-0.2,0.27),(-0.621,0.2,0.27),ang,cx,cy,"#20240b"))
        out.append(line3((-0.621,-0.05,0.21),(-0.621,0.05,0.21),ang,cx,cy,"#8a8d8f",4))
    return out
def turret_body_details(nrm,nr,ang,cx,cy):
    out=[]
    if nrm==(0,0,1):
        out.append(circle3((-0.08,0.07,0.441),0.055,"xy",ang,cx,cy,"#4B5320",light(nr)*0.92))
        out.append(circle3((-0.08,-0.08,0.441),0.03,"xy",ang,cx,cy,"#3d4419",light(nr)))
    if nrm==(1,0,0):
        out.append(line3((0.161,-0.12,0.42),(0.161,-0.05,0.42),ang,cx,cy,"#111",4))
    return out
TEX=('<filter id="tex" x="0" y="0" width="100%" height="100%">'
 '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>'
 '<feColorMatrix in="n" type="matrix" values="1.6 0 0 0 -0.3  1.6 0 0 0 -0.3  1.6 0 0 0 -0.3  0 0 0 0 0.55" result="grain"/>'
 '<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="3" result="m"/>'
 '<feColorMatrix in="m" type="matrix" values="0 0 0 0 0.22  0 0 0 0 0.18  0 0 0 0 0.1  0 0 0 0.9 -0.38" result="grime"/>'
 '<feComposite in="grain" in2="SourceAlpha" operator="in" result="g2"/>'
 '<feComposite in="grime" in2="SourceAlpha" operator="in" result="m2"/>'
 '<feBlend in="SourceGraphic" in2="g2" mode="overlay" result="a"/>'
 '<feComposite in="m2" in2="a" operator="over"/>'
 '</filter>')
def hull_svg(yaw):
    a=math.radians(yaw); cx=cy=SIZE/2; out=[]
    parts=D.tank_parts()
    hc=D.depth(D.rot((0,0,0.15),a))
    att=[(D.depth(D.rot(((p["b"][0]+p["b"][1])/2,0,0.15),a)),p,(blade_details if i==0 else box_details)) for i,p in enumerate(D.ATTACH)]
    for d0,p,f in att:
        if d0<hc: out+=part_svg(p,a,cx,cy,f)
    out+=part_svg(parts[0],a,cx,cy,track_details(-1))
    out+=part_svg(parts[1],a,cx,cy,track_details(1))
    out+=part_svg(parts[2],a,cx,cy,deck_details)
    for d0,p,f in att:
        if d0>=hc: out+=part_svg(p,a,cx,cy,f)
    return out
PIVOT_Z=0.365
def turret_svg(yaw):
    a=math.radians(yaw); cx=SIZE/2; cy=SIZE/2+PIVOT_Z*math.cos(D.E)*S
    body,band,barrel=D.TURRET[0],D.TURRET[1],D.TURRET[2]
    def dep(p):
        b=p["b"]; return D.depth(D.rot(((b[0]+b[1])/2,(b[2]+b[3])/2,(b[4]+b[5])/2),a))
    seq=[barrel,body,band] if dep(barrel)<dep(body) else [body,band,barrel]
    out=[]
    for p in seq: out+=part_svg(p,a,cx,cy,turret_body_details if p is body else None)
    return out
def save(name,polys):
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
       f'<defs>{TEX}{"".join(defs)}</defs><rect width="100%" height="100%" fill="{BG}"/>'
       f'<g>{"".join(polys)}</g></svg>')
    open(name,"w").write(s); defs.clear()
if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out,exist_ok=True)
    for n,y in DIRS:
        save(os.path.join(out,f"guide2_hull_{n}.svg"),hull_svg(y))
        save(os.path.join(out,f"guide2_turret_{n}.svg"),turret_svg(y))
