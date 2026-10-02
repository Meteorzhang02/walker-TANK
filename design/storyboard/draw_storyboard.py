import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "character"))
import draw_sketches as D
W,H=640,360
FONT='font-family="DejaVu Sans, Arial, sans-serif"'
def setE(deg):
    D.E=math.radians(deg); D.V=(0,math.cos(D.E),math.sin(D.E))
def P(x,y,z,S,cx,cy): return D.proj((x,y,z),S,cx,cy)
def box(x,y,w,d,h,color,S,cx,cy,crack=False):
    b=(x-w/2,x+w/2,y-d/2,y+d/2,0,h); out=[]
    for nrm,pts in D.faces(b):
        if sum(nrm[i]*D.V[i] for i in range(3))<=1e-6: continue
        lam=max(0,sum(nrm[i]*D.L[i] for i in range(3)))
        pts2=" ".join("%.1f,%.1f"%P(*p,S,cx,cy) for p in pts)
        out.append(f'<polygon points="{pts2}" fill="{D.shade(color,0.55+0.6*lam)}" stroke="#2a211b" stroke-width="1"/>')
    if crack:
        a=P(x-w/3,y+d/2,h*0.9,S,cx,cy); b2=P(x,y+d/2,h*0.5,S,cx,cy); c=P(x+w/4,y+d/2,h*0.15,S,cx,cy)
        out.append(f'<polyline points="{a[0]:.1f},{a[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {c[0]:.1f},{c[1]:.1f}" fill="none" stroke="#111" stroke-width="2"/>')
    return "".join(out)
def tank(x,y,yaw,S,cx,cy,tyaw=None,enemy=False,wreck=False):
    sx,sy=P(x,y,0,S,cx,cy)
    s=D.draw_tank(yaw,S,sx,sy,turret_yaw_deg=tyaw)
    if enemy: s=s.replace(D.shade(D.OLIVE,1)[:1],"#")  # no-op
    if enemy or wreck:
        # recolor olive faces to enemy grey / wreck black by filter group
        f="url(#enemy)" if enemy else "url(#wreck)"
        s=f'<g filter="{f}">{s}</g>'
    return s
DEFS='''<defs>
<filter id="enemy"><feColorMatrix type="matrix" values="0.45 0.45 0.1 0 0  0.4 0.4 0.1 0 0  0.4 0.4 0.15 0 0  0 0 0 1 0"/></filter>
<filter id="wreck"><feColorMatrix type="matrix" values="0.12 0.12 0.05 0 0  0.1 0.1 0.05 0 0  0.09 0.09 0.05 0 0  0 0 0 1 0"/></filter>
<marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ffd34d"/></marker>
</defs>'''
def burst(x,y,r,col1="#ff9a2e",col2="#ffe27a"):
    pts=[]
    for i in range(16):
        a=i*math.pi/8; rr=r if i%2==0 else r*0.55
        pts.append(f"{x+rr*math.cos(a):.1f},{y+rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{col1}" stroke="#b34700"/><circle cx="{x}" cy="{y}" r="{r*0.35:.1f}" fill="{col2}"/>'
def smoke(x,y,s):
    return "".join(f'<circle cx="{x+dx*s:.1f}" cy="{y-dy*s:.1f}" r="{rr*s:.1f}" fill="#6b6b6b" opacity="0.75"/>' for dx,dy,rr in [(0,0,10),(6,14,12),(-4,28,14),(8,44,15)])
def arrow(x1,y1,x2,y2,dash=False):
    d=' stroke-dasharray="7 5"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ffd34d" stroke-width="3"{d} marker-end="url(#ar)"/>'
def label(n,shot,cap):
    return (f'<rect x="0" y="0" width="{W}" height="26" fill="rgba(0,0,0,0.6)"/>'
            f'<text x="10" y="18" {FONT} font-size="14" fill="#fff" font-weight="bold">{n}</text>'
            f'<text x="40" y="18" {FONT} font-size="13" fill="#ddd">{shot}</text>'
            f'<rect x="0" y="{H-26}" width="{W}" height="26" fill="rgba(0,0,0,0.6)"/>'
            f'<text x="10" y="{H-9}" {FONT} font-size="13" fill="#fff">{cap}</text>')
def txt(x,y,t,size=13,col="#ffd34d"):
    return f'<text x="{x}" y="{y}" {FONT} font-size="{size}" fill="{col}" font-weight="bold">{t}</text>'
def frame(body,name,bg="#5a4a3a"):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}<rect width="100%" height="100%" fill="{bg}"/>{body}</svg>'
    open(f"sb_{name}.svg","w").write(s)
BRICK="#7a5c4a"
panels=[]
# 1 opening
setE(90); S=34; b=""
for (x,y) in [(-6,-2),(-3,1.5),(0,-1),(3,2),(5,-2.5),(-1,3),(2,-3)]:
    b+=box(x,y,1.4,0.6,0.5,BRICK,S,320,190)
for (x,y,yw) in [(-5,-3.5,90),(4,-3.6,135),(6.5,0.5,180)]:
    b+=tank(x,y,yw,S,320,190,enemy=True)
b+=tank(-6.5,3.2,-45,S,320,190)
b+=f'<rect x="{320-6.5*S-45}" y="{190+3.2*S-45}" width="90" height="70" fill="none" stroke="#ffd34d" stroke-width="2" stroke-dasharray="6 4"/>'
b+=arrow(500,80,140,280,True)+txt(390,70,"camera zooms in")
b+=label("1","EXTREME WIDE · TOP-DOWN · zoom (motion)","First sight: whole map, then zoom to YunqiZ. Music starts.")
frame(b,"01-opening")
# 2 fire from cover
setE(55); S=110; cx,cy=320,200; b=""
b+=box(0.2,0,0.5,1.5,0.35,BRICK,S,cx,cy)
b+=tank(-1.3,0.2,0,S,cx,cy,tyaw=-10)
b+=tank(2.2,-0.8,180,S*0.7,cx+40,cy-10,enemy=True)
mx,my=P(-1.3+0.82,0.2-0.14,0.38,S,cx,cy)
b+=burst(mx,my,22)
b+=f'<line x1="{mx+20}" y1="{my-4}" x2="{cx+140}" y2="{cy-55}" stroke="#ffe27a" stroke-width="2" stroke-dasharray="5 6"/>'
b+=arrow(130,250,80,250)+txt(60,280,"recoil")+txt(mx-10,my-30,"muzzle flash")
b+=label("2","MEDIUM · HIGH OBLIQUE · flash + recoil (motion)","Core action: aim from behind cover and fire. SFX-fire.")
frame(b,"02-fire-from-cover")
# 3 cover breaking
b=""; S=100
b+=box(-0.3,0.1,0.5,1.4,0.35,BRICK,S,cx,cy,crack=True)
b+=box(-0.15,-0.35,0.25,0.3,0.12,BRICK,S,cx,cy)
b+=box(1.9,1.0,0.5,1.4,0.35,BRICK,S,cx,cy)
b+=tank(-1.4,0.4,30,S,cx,cy,tyaw=0)
for yy in (-90,-60):
    b+=f'<line x1="{cx+300}" y1="{cy+yy}" x2="{cx+10}" y2="{cy+yy+60}" stroke="#ff7b54" stroke-width="2" stroke-dasharray="5 6"/>'
b+=arrow(cx-150,cy+70,cx+120,cy+110)+txt(cx-60,cy+130,"move to next cover")+txt(cx-40,cy-80,"cracks!",13,"#ff7b54")
b+=label("3","MEDIUM · HIGH OBLIQUE · movement (motion)","Decision: cover is cracking, relocate. SFX-cover-hit.")
frame(b,"03-cover-breaking")
# 4 enemy destroyed close-up
b=""; S=260
b+=tank(0,0.1,200,S,cx,cy+10,enemy=True)
b+=burst(cx+10,cy-30,95)
for dx,dy in [(-170,-60),(160,-80),(-120,60),(150,50)]:
    b+=f'<rect x="{cx+dx}" y="{cy+dy}" width="10" height="6" fill="#2a2a2a" transform="rotate({dx%37} {cx+dx} {cy+dy})"/>'
b+=f'<path d="M20,60 l10,0 M20,70 l14,0 M606,60 l14,0 M610,70 l10,0" stroke="#ffd34d" stroke-width="3"/>'+txt(30,55,"camera shake")
b+=label("4","CLOSE-UP · HIGH OBLIQUE · camera shake (motion)","Success: enemy tank explodes, leaves a wreck. SFX-explode.")
frame(b,"04-enemy-destroyed")
# 5 damage close-up
b=""; S=240
b+=tank(0,0.1,0,S,cx-60,cy+30,tyaw=-20)
b+=smoke(cx-110,cy-30,2.2)
b+=burst(cx-20,cy-20,26,"#ff5a1f","#ffc04d")
b+=f'<rect x="440" y="40" width="180" height="18" fill="#222" stroke="#ddd"/><rect x="442" y="42" width="45" height="14" fill="#c0392b"/>'+txt(440,75,"health low",12,"#fff")
b+=label("5","CLOSE-UP · HIGH OBLIQUE","Damage: hit flash, then smoke / fire on the tank. SFX-player-hit.")
frame(b,"05-damage")
# 6 failure
b=""; S=120
b+=box(1.3,-0.2,0.5,1.4,0.35,BRICK,S,cx,cy)
b+=tank(-0.6,0.3,20,S,cx,cy,wreck=True)
b+=burst(cx-70,cy-10,70)+smoke(cx-90,cy-70,1.5)
b+=txt(410,70,"music stops",14,"#fff")+txt(410,90,"(explosion tail only)",12,"#ddd")
b+=label("6","MEDIUM · HIGH OBLIQUE","Failure: YunqiZ destroyed. Music cuts to silence.")
frame(b,"06-failure")
# 7 respawn wide
b=""; S=48; cx2,cy2=320,190
for (x,y) in [(-4,-1),(-1,1.2),(2,-1.5),(4.5,1.5)]:
    b+=box(x,y,1.2,0.5,0.35,BRICK,S,cx2,cy2)
b+=tank(-1,-2.8,90,S,cx2,cy2,wreck=True)+tank(3.5,-2.5,120,S,cx2,cy2,wreck=True)
for wx,wy in [(-1,-2.8),(3.5,-2.5)]:
    px,py=P(wx,wy,0.4,S,cx2,cy2); b+=smoke(px,py,0.9)+txt(px-18,py+34,"wreck",11,"#ddd")
b+=tank(5.5,-0.2,180,S,cx2,cy2,enemy=True)
b+=tank(-5.2,1.9,-30,S,cx2,cy2)
sx,sy=P(-5.2,1.9,0,S,cx2,cy2)
b+=f'<ellipse cx="{sx}" cy="{sy}" rx="45" ry="26" fill="none" stroke="#7ee0a0" stroke-width="2" stroke-dasharray="5 4"/>'+txt(sx-40,sy+48,"spawn point",12,"#7ee0a0")
b+=txt(300,200,"wrecks stay = progress kept",12,"#fff")
b+=label("7","WIDE · HIGH OBLIQUE","Retry: respawn at spawn, full health. Music restarts.")
frame(b,"07-respawn")
# 8 victory low angle
setE(15); b=""; S=300
b+=f'<rect width="{W}" height="{H}" fill="#3d3a36"/>'
sx,sy=320,250
b+=D.draw_tank(60,S,sx,sy,turret_yaw_deg=25)
tx,ty=D.proj((-0.02,0,0.44),S,sx,sy)
b+=f'<line x1="{tx}" y1="{ty}" x2="{tx}" y2="{ty-120}" stroke="#ccc" stroke-width="3"/><rect x="{tx}" y="{ty-120}" width="60" height="34" fill="#E8E6DF" stroke="#999"/>'
b+=f'<rect x="20" y="40" width="210" height="130" fill="rgba(0,0,0,0.65)" stroke="#E8E6DF"/>'+txt(40,80,"VICTORY",28,"#E8E6DF")+txt(40,110,"enemies destroyed: 3/3",13,"#ddd")+txt(40,132,"time: 4:52",13,"#ddd")+txt(40,154,"[ retry ]  [ quit ]",13,"#ffd34d")
b+=label("8","CLOSE-UP · LOW ANGLE (victory-screen illustration)","End: victory screen. Music stops, SFX-victory.")
frame(b,"08-victory",bg="#3d3a36")
