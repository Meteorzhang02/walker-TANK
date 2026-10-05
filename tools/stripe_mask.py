"""Render the white-stripe mask for each turret direction from the v3 turret guide geometry
(the stripe position is the same in v3 and v3.1). Written by Claude."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "design", "guides", "v3"))
import draw_guides_v3 as G3
G=G3.G; D=G.D
_poly=G.poly
def poly_mask(pts3, ang, cx, cy, color, k, edge=True):
    if color==D.WHITE:
        p2=[D.proj(D.rot(q,ang),G.S,cx,cy) for q in pts3]
        return f'<polygon points="{" ".join("%.1f,%.1f"%p for p in p2)}" fill="#ff0000" stroke="none"/>'
    return f'<polygon points="{" ".join("%.1f,%.1f"%D.proj(D.rot(q,ang),G.S,cx,cy) for q in pts3)}" fill="#000000"/>'
G.poly=poly_mask
_bar=G3.barrel_svg
def barrel_black(ang,cx,cy):
    return [s.replace('fill="url(#','fill="#000000" data-x="').replace('fill="#3a3d40"','fill="#000000"').replace('fill="#050505"','fill="#000000"') for s in _bar(ang,cx,cy)]
G3.barrel_svg=barrel_black
G3.hatch_svg=lambda *a,**k: []
G.circle3=lambda *a,**k: ""
G.line3=lambda *a,**k: ""
if __name__=="__main__":
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    for n,y in G.DIRS:
        G.save(os.path.join(out,f"stripe_mask_{n}.svg"),G3.turret_svg(y))
