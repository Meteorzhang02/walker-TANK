import math
E = math.radians(55)            # camera elevation
L = (-1,-1,2); n=math.sqrt(sum(c*c for c in L)); L=tuple(c/n for c in L)
V = (0, math.cos(E), math.sin(E))  # toward camera
OLIVE="#4B5320"; DARK="#2F3234"; WORN="#7D8084"; TRACK="#1E1F1F"; WHITE="#E8E6DF"

def box(x0,x1,y0,y1,z0,z1,color):
    return dict(b=(x0,x1,y0,y1,z0,z1),c=color)

def tank_parts(turret_yaw=0):
    parts=[
      box(-0.50,0.50,-0.31,-0.13,0.0,0.20,TRACK),
      box(-0.50,0.50, 0.13, 0.31,0.0,0.20,TRACK),
      box(-0.47,0.47,-0.32, 0.32,0.20,0.29,OLIVE),
    ]
    return parts
ATTACH=[box(0.52,0.60,-0.37,0.37,0.02,0.20,WORN),      # front dozer blade
        box(-0.62,-0.47,-0.22,0.22,0.14,0.31,"#3d4419")]  # rear storage box
TURRET=[box(-0.20,0.16,-0.17,0.17,0.29,0.44,OLIVE),
        box(-0.205,0.165,-0.175,0.175,0.36,0.395,WHITE),
        box(0.16,0.78,-0.03,0.03,0.35,0.40,DARK)]

def faces(b):
    x0,x1,y0,y1,z0,z1=b
    P=lambda x,y,z:(x,y,z)
    return [
     ((1,0,0),[P(x1,y0,z0),P(x1,y1,z0),P(x1,y1,z1),P(x1,y0,z1)]),
     ((-1,0,0),[P(x0,y0,z0),P(x0,y1,z0),P(x0,y1,z1),P(x0,y0,z1)]),
     ((0,1,0),[P(x0,y1,z0),P(x1,y1,z0),P(x1,y1,z1),P(x0,y1,z1)]),
     ((0,-1,0),[P(x0,y0,z0),P(x1,y0,z0),P(x1,y0,z1),P(x0,y0,z1)]),
     ((0,0,1),[P(x0,y0,z1),P(x1,y0,z1),P(x1,y1,z1),P(x0,y1,z1)]),
    ]
def rot(p,a):
    c,s=math.cos(a),math.sin(a); x,y,z=p
    return (x*c-y*s, x*s+y*c, z)
def shade(hexc,k):
    r,g,b=[int(hexc[i:i+2],16) for i in (1,3,5)]
    f=lambda v:max(0,min(255,int(v*k)))
    return "#%02x%02x%02x"%(f(r),f(g),f(b))
def proj(p,S,cx,cy):
    x,y,z=p
    return (cx+x*S, cy+(y*math.sin(E)-z*math.cos(E))*S)
def depth(p): return p[1]*math.cos(E)+p[2]*math.sin(E)

def draw_tank(yaw_deg,S,cx,cy,silhouette=False,turret_yaw_deg=None):
    a=math.radians(yaw_deg); ta=math.radians(turret_yaw_deg if turret_yaw_deg is not None else yaw_deg)
    groups=[]
    for part,ang in [(p,a) for p in tank_parts()]:
        groups.append(("hull",part,ang))
    turret_groups=[(("tur",p,ta)) for p in TURRET]
    out=[]
    def render(part,ang):
        polys=[]
        for nrm,pts in faces(part["b"]):
            if part["c"]==WHITE and nrm==(0,0,1): continue
            nr=rot(nrm,ang)
            if sum(nr[i]*V[i] for i in range(3))<=1e-6: continue
            rp=[rot(p,ang) for p in pts]
            lam=max(0,sum(nr[i]*L[i] for i in range(3)))
            col="#000" if silhouette else shade(part["c"],0.55+0.6*lam)
            d=sum(depth(p) for p in rp)/4
            pts2=" ".join("%.1f,%.1f"%proj(p,S,cx,cy) for p in rp)
            stroke="#000" if silhouette else "#141515"
            polys.append((d,f'<polygon points="{pts2}" fill="{col}" stroke="{stroke}" stroke-width="{max(0.5,S/160):.2f}" stroke-linejoin="round"/>'))
        return polys
    # hull: tracks then deck
    hc=depth(rot((0,0,0.15),a))
    att=[(depth(rot(((p["b"][0]+p["b"][1])/2,0,0.15),a)),p) for p in ATTACH]
    for d0,p in att:
        if d0<hc:
            for d,s in sorted(render(p,a)): out.append(s)
    for _,p,ang in groups:
        for d,s in sorted(render(p,ang)): out.append(s)
    for d0,p in att:
        if d0>=hc:
            for d,s in sorted(render(p,a)): out.append(s)
    # turret parts sorted by centroid depth
    tp=[]
    for _,p,ang in turret_groups:
        b=p["b"]; c=rot(((b[0]+b[1])/2,(b[2]+b[3])/2,(b[4]+b[5])/2),ang)
        tp.append((depth(c),p,ang))
    tp.sort(key=lambda t:t[0])
    # white band must draw right after turret body
    body=[t for t in tp if t[1]["c"]==OLIVE]; band=[t for t in tp if t[1]["c"]==WHITE]; barrel=[t for t in tp if t[1]["c"]==DARK]
    order = (barrel+body+band) if barrel[0][0]<body[0][0] else (body+band+barrel)
    for _,p,ang in order:
        for d,s in sorted(render(p,ang)): out.append(s)
    return "\n".join(out)

DIRS=[("up",-90),("up-right",-45),("right",0),("down-right",45),("down",90)]
def ground_y(cy): return cy
def svg(w,h,body,bg):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="{bg}"/>{body}<text/></svg>'
FONT='font-family="DejaVu Sans, Arial, sans-serif"'

# turnaround
S=200; W=1300; H=430; body=[]
top_y=240-0.44*math.cos(E)*S
body.append(f'<text x="20" y="40" {FONT} font-size="26" font-weight="bold" fill="#222">YunqiZ — turnaround (5 generated directions)</text>')
body.append(f'<line x1="70" y1="{top_y:.1f}" x2="{W-20}" y2="{top_y:.1f}" stroke="#c0392b" stroke-dasharray="6 5"/>')
body.append(f'<line x1="70" y1="240" x2="{W-20}" y2="240" stroke="#2c6fbb" stroke-dasharray="6 5"/>')
body.append(f'<text x="18" y="{top_y+5:.1f}" {FONT} font-size="13" fill="#c0392b">turret top</text>')
body.append(f'<text x="18" y="245" {FONT} font-size="13" fill="#2c6fbb">hull centre</text>')
for i,(name,yaw) in enumerate(DIRS):
    cx=180+i*240
    body.append(draw_tank(yaw,S,cx,240))
    body.append(f'<text x="{cx}" y="{360}" {FONT} font-size="20" text-anchor="middle" fill="#222">{name}</text>')
body.append(f'<text x="20" y="410" {FONT} font-size="15" fill="#444">Mirrored at runtime: up-left, left, down-left. Rough code-drawn sketch by Claude (not a generative-model asset).</text>')
open("turnaround.svg","w").write(svg(W,H,"".join(body),"#f4f2ec"))

# silhouette
W=1300;H=540; body=[]
body.append(f'<text x="20" y="38" {FONT} font-size="24" font-weight="bold" fill="#111">YunqiZ — silhouette test</text>')
body.append(f'<text x="20" y="80" {FONT} font-size="15" fill="#111">Actual game size (about 64 px across the hull):</text>')
for i,(name,yaw) in enumerate(DIRS):
    body.append(draw_tank(yaw,64,80+i*120,140,silhouette=True))
body.append(f'<text x="20" y="215" {FONT} font-size="15" fill="#111">Same silhouettes enlarged 2.5x for inspection:</text>')
for i,(name,yaw) in enumerate(DIRS):
    cx=140+i*250
    body.append(draw_tank(yaw,160,cx,380,silhouette=True))
    body.append(f'<text x="{cx}" y="510" {FONT} font-size="16" text-anchor="middle" fill="#111">{name}</text>')
open("silhouette.svg","w").write(svg(W,H,"".join(body),"#8a8a8a"))

# collision
S=200; W=1300; H=430; body=[]
body.append(f'<text x="20" y="40" {FONT} font-size="26" font-weight="bold" fill="#222">YunqiZ — collision overlay (circle, r = half hull width)</text>')
r=0.32*S
for i,(name,yaw) in enumerate(DIRS):
    cx=180+i*240; cy=240
    body.append(draw_tank(yaw,S,cx,cy))
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="rgba(46,204,113,0.18)" stroke="#1e9e57" stroke-width="3"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#1e9e57"/>')
    body.append(f'<text x="{cx}" y="360" {FONT} font-size="20" text-anchor="middle" fill="#222">{name}</text>')
body.append(f'<text x="20" y="400" {FONT} font-size="15" fill="#444">Green circle = planned collision, centred on the hull on the ground plane. Barrel and hull corners outside the circle do not take hits.</text>')
open("collision.svg","w").write(svg(W,H,"".join(body),"#f4f2ec"))
