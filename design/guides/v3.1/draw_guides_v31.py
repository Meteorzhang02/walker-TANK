"""Turret guides v3.1 for YunqiZ: same as v3 but with a large domed commander cupola,
sized to match the dome SDXL produced on the up-right and down-right turrets at denoise 0.60.
Used for the up, right and down turrets. Code-drawn by Claude (not generative-model output)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v3"))
import draw_guides_v3 as G3
G=G3.G; D=G.D
def ring(cxw,cyw,r,z,ang,cx,cy,n=32):
    return [D.proj(D.rot((cxw+r*math.cos(2*math.pi*i/n), cyw+r*math.sin(2*math.pi*i/n), z),ang),G.S,cx,cy) for i in range(n)]
def P(pts): return " ".join("%.1f,%.1f"%p for p in pts)
def cupola_svg(ang,cx,cy,k):
    cxw,cyw=-0.03,0.0
    tiers=[(0.115,0.440,0.470,0.60),(0.100,0.470,0.490,0.75),(0.075,0.490,0.502,0.90)]
    out=[]
    for r,z0,z1,kk in tiers:
        side=G3.hull2d([(round(p[0],1),round(p[1],1)) for p in ring(cxw,cyw,r,z0,ang,cx,cy)+ring(cxw,cyw,r,z1,ang,cx,cy)])
        out.append(f'<polygon points="{P(side)}" fill="{D.shade("#4B5320",kk)}" stroke="#2c3112" stroke-width="1.5"/>')
    top=ring(cxw,cyw,0.075,0.502,ang,cx,cy)
    out.append(f'<polygon points="{P(top)}" fill="{G.grad_fill("#4B5320",k*1.08,top)}" stroke="#6b7536" stroke-width="1.5"/>')
    hatch=ring(cxw,cyw+0.01,0.03,0.503,ang,cx,cy,20)
    out.append(f'<polygon points="{P(hatch)}" fill="{D.shade("#4B5320",0.8)}" stroke="#2c3112" stroke-width="2"/>')
    return out
G3.hatch_svg=cupola_svg
if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out,exist_ok=True)
    for n,y in G.DIRS:
        G.save(os.path.join(out,f"guide31_turret_{n}.svg"),G3.turret_svg(y))
