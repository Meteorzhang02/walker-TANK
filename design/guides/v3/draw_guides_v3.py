"""Turret img2img guides v3 for YunqiZ: round barrel with muzzle opening and a raised hatch.
Code-drawn by Claude (not generative-model output). Hull guides stay at v2.
Same scale, view and pivot as v1/v2, so turret v3 still lines up with the hull."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2"))
import draw_guides_v2 as G
D=G.D
BAR_R=0.032; BAR_X0=0.12; BAR_X1=0.78; BAR_Z=0.375
def hull2d(pts):
    pts=sorted(set(pts))
    if len(pts)<3: return pts
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def ring_x(x, r, ang, cx, cy, n=28):  # circle in the y-z plane at position x (barrel cross-section)
    return [D.proj(D.rot((x, r*math.cos(2*math.pi*i/n), BAR_Z + r*math.sin(2*math.pi*i/n)),ang),G.S,cx,cy) for i in range(n)]
def barrel_svg(ang,cx,cy):
    a=ring_x(BAR_X0,BAR_R,ang,cx,cy); b=ring_x(BAR_X1,BAR_R,ang,cx,cy)
    h=hull2d([(round(p[0],1),round(p[1],1)) for p in a+b])
    p0=D.proj(D.rot((BAR_X0,0,BAR_Z),ang),G.S,cx,cy); p1=D.proj(D.rot((BAR_X1,0,BAR_Z),ang),G.S,cx,cy)
    ax,ay=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(ax,ay) or 1
    nx,ny=-ay/L,ax/L
    if ny>0: nx,ny=-nx,-ny          # gradient runs from the lit (upper) side to the shadow side
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2; w=BAR_R*G.S
    G.gid[0]+=1; i=f"g{G.gid[0]}"
    G.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{mx+nx*w:.1f}" y1="{my+ny*w:.1f}" x2="{mx-nx*w:.1f}" y2="{my-ny*w:.1f}">'
                  f'<stop offset="0" stop-color="#7a7e82"/><stop offset="0.35" stop-color="#4a4e52"/><stop offset="1" stop-color="#1c1e20"/></linearGradient>')
    out=[f'<polygon points="{" ".join("%.1f,%.1f"%p for p in h)}" fill="url(#{i})" stroke="#5a5e62" stroke-width="1.5"/>']
    # muzzle ring + bore, if the barrel end faces the camera
    axis=D.rot((1,0,0),ang)
    if sum(axis[k]*D.V[k] for k in range(3))>0.02:
        out.append(f'<polygon points="{" ".join("%.1f,%.1f"%p for p in b)}" fill="#3a3d40" stroke="#6a6e72" stroke-width="1.5"/>')
        bore=ring_x(BAR_X1+0.001,BAR_R*0.55,ang,cx,cy)
        out.append(f'<polygon points="{" ".join("%.1f,%.1f"%p for p in bore)}" fill="#050505"/>')
    else:
        # thicker muzzle collar seen from the side
        c0=ring_x(BAR_X1-0.05,BAR_R*1.25,ang,cx,cy); c1=ring_x(BAR_X1,BAR_R*1.25,ang,cx,cy)
        hc=hull2d([(round(p[0],1),round(p[1],1)) for p in c0+c1])
        out.append(f'<polygon points="{" ".join("%.1f,%.1f"%p for p in hc)}" fill="url(#{i})" stroke="#5a5e62" stroke-width="1.5"/>')
    return out
def hatch_svg(ang,cx,cy,k):
    cxw,cyw,r,z0,z1=-0.08,0.07,0.06,0.44,0.475
    def ring(z): return [D.proj(D.rot((cxw+r*math.cos(2*math.pi*i/28), cyw+r*math.sin(2*math.pi*i/28), z),ang),G.S,cx,cy) for i in range(28)]
    side=hull2d([(round(p[0],1),round(p[1],1)) for p in ring(z0)+ring(z1)])
    top=ring(z1)
    out=[f'<polygon points="{" ".join("%.1f,%.1f"%p for p in side)}" fill="{D.shade("#4B5320",0.62)}" stroke="#2c3112" stroke-width="1.5"/>',
         f'<polygon points="{" ".join("%.1f,%.1f"%p for p in top)}" fill="{G.grad_fill("#4B5320",k*1.05,top)}" stroke="#6b7536" stroke-width="1.5"/>']
    # hinge
    h0=D.proj(D.rot((cxw-r,cyw-0.02,z1),ang),G.S,cx,cy); h1=D.proj(D.rot((cxw-r,cyw+0.02,z1),ang),G.S,cx,cy)
    out.append(f'<line x1="{h0[0]:.1f}" y1="{h0[1]:.1f}" x2="{h1[0]:.1f}" y2="{h1[1]:.1f}" stroke="#20240b" stroke-width="5" stroke-linecap="round"/>')
    return out
def body_details(nrm,nr,ang,cx,cy):
    out=[]
    if nrm==(0,0,1):
        out+=hatch_svg(ang,cx,cy,G.light(nr))
        out.append(G.circle3((-0.08,-0.09,0.441),0.028,"xy",ang,cx,cy,"#3d4419",G.light(nr)))
    if nrm==(1,0,0):
        out.append(G.line3((0.161,-0.13,0.425),(0.161,-0.06,0.425),ang,cx,cy,"#111",4))
    return out
def turret_svg(yaw):
    a=math.radians(yaw); cx=G.SIZE/2; cy=G.SIZE/2+G.PIVOT_Z*math.cos(D.E)*G.S
    body,band=D.TURRET[0],D.TURRET[1]
    bd=D.depth(D.rot((-0.02,0,0.365),a)); brd=D.depth(D.rot(((BAR_X0+BAR_X1)/2,0,BAR_Z),a))
    out=[]
    if brd<bd: out+=barrel_svg(a,cx,cy)
    out+=G.part_svg(body,a,cx,cy,body_details)
    out+=G.part_svg(band,a,cx,cy,None)
    if brd>=bd: out+=barrel_svg(a,cx,cy)
    return out
if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out,exist_ok=True)
    for n,y in G.DIRS:
        G.save(os.path.join(out,f"guide3_turret_{n}.svg"),turret_svg(y))
