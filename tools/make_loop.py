"""Cut a seamless music loop from a generated track (written by Claude).
Edits: find the start point (within the steady middle section) where the audio after start and
after start+L match best, with L = a whole number of bars at the detected tempo; cut [start, start+L);
blend the last XF ms with the audio that leads into the start point (equal-power crossfade), so the
end flows into the start; normalise to -1 dBFS peak; write OGG Vorbis (q6) and a 3x preview."""
import sys, subprocess, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from process_sfx import load
def best_start(m, sr, L, lo, hi, win_s=0.25):
    w=int(win_s*sr); best=(-2,None); step=int(0.002*sr)
    for s in range(int(lo*sr), int(hi*sr), step):
        e=s+L
        a=m[s:s+w]; b=m[e:e+w]; c=m[s-w:s]; d=m[e-w:e]
        sc=(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)+1e-12)+np.dot(c,d)/np.sqrt(np.dot(c,c)*np.dot(d,d)+1e-12))/2
        if sc>best[0]: best=(sc,s)
    # refine at sample level
    s0=best[1]; bb=best
    for s in range(s0-step, s0+step):
        e=s+L; a=m[s:s+w]; b=m[e:e+w]; c=m[s-w:s]; d=m[e-w:e]
        sc=(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)+1e-12)+np.dot(c,d)/np.sqrt(np.dot(c,c)*np.dot(d,d)+1e-12))/2
        if sc>bb[0]: bb=(sc,s)
    return bb
def write(y,sr,dst,codec):
    args=["ffmpeg","-v","error","-y","-f","f32le","-ar",str(sr),"-ac",str(y.shape[1]),"-i","-"]+codec+[dst]
    subprocess.run(args,input=y.astype(np.float32).tobytes(),check=True)
def make(src, dst, bpm, bars, lo, hi, xf_ms=150, peak_db=-1.0):
    x,sr=load(src); m=x.mean(axis=1)
    L=int(round(bars*4*60/bpm*sr))
    score,s=best_start(m,sr,L,lo,hi)
    e=s+L; xf=int(xf_ms/1000*sr)
    y=x[s:e].copy()
    t=np.linspace(0,np.pi/2,xf)[:,None]
    y[-xf:]=x[e-xf:e]*np.cos(t)+x[s-xf:s]*np.sin(t)
    y*=10**(peak_db/20)/np.abs(y).max()
    write(y,sr,dst,["-c:a","libvorbis","-q:a","6"])
    write(np.concatenate([y,y,y]),sr,dst.replace(".ogg","_3x_preview.ogg"),["-c:a","libvorbis","-q:a","6"])
    # seam check: jump between last and first sample vs typical sample-to-sample step
    jump=np.abs(y[0]-y[-1]).max(); typ=np.percentile(np.abs(np.diff(y,axis=0)),99)
    return {"start_s":round(s/sr,4),"end_s":round(e/sr,4),"length_s":round(L/sr,4),"bars":bars,"bpm":bpm,
            "match_score":round(float(score),3),"seam_jump":round(float(jump),4),"p99_step":round(float(typ),4)}
if __name__=="__main__":
    src,dst=sys.argv[1],sys.argv[2]
    print(make(src,dst,bpm=float(sys.argv[3]),bars=int(sys.argv[4]),lo=float(sys.argv[5]),hi=float(sys.argv[6])))
