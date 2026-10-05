"""Trim and normalise a generated one-shot sound effect for Godot (written by Claude).
Edits: cut leading silence (keeps 5 ms before the onset), cut the tail once the level stays
below -60 dB relative to the peak, apply a 30 ms fade-out, normalise the peak to -1 dBFS,
write 16-bit 44.1 kHz WAV."""
import sys, subprocess, numpy as np, json
def load(path):
    st=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",path]))["streams"][0]
    sr=int(st["sample_rate"]); ch=int(st["channels"])
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",path,"-f","f32le","-acodec","pcm_f32le","-"])
    return np.frombuffer(raw,dtype=np.float32).reshape(-1,ch).copy(),sr
def process(src,dst,tail_db=-60.0,fade_ms=30,peak_db=-1.0):
    x,sr=load(src); m=np.abs(x).max(axis=1)
    win=int(0.01*sr); env=np.sqrt(np.convolve(m**2,np.ones(win)/win,'same')); db=20*np.log10(env+1e-9); top=db.max()
    on=max(0,int(np.argmax(db>top-40))-int(0.005*sr))
    above=np.where(db>top+tail_db)[0]; end=min(len(x),int(above[-1])+int(0.02*sr))
    y=x[on:end].copy(); f=int(fade_ms/1000*sr); y[-f:]*=np.linspace(1,0,f)[:,None]
    y*=10**(peak_db/20)/max(np.abs(y).max(),1e-9)
    p=subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(sr),"-ac",str(x.shape[1]),"-i","-","-acodec","pcm_s16le",dst],input=y.astype(np.float32).tobytes())
    return {"src":src,"dst":dst,"start_s":round(on/sr,3),"end_s":round(end/sr,3),"length_s":round(len(y)/sr,3)}
if __name__=="__main__":
    print(process(sys.argv[1],sys.argv[2]))
