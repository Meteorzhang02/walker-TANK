"""Analyse a generated sound effect: settings from ComfyUI metadata, envelope, spectrum, clipping.
Written by Claude."""
import sys, json, subprocess, numpy as np
def load(path):
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",path]))
    st=info["streams"][0]; sr=int(st["sample_rate"]); ch=int(st["channels"])
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",path,"-f","f32le","-acodec","pcm_f32le","-"])
    x=np.frombuffer(raw,dtype=np.float32).reshape(-1,ch)
    tags=info["format"].get("tags",{})
    return x,sr,tags
def settings(tags):
    p=json.loads(tags.get("prompt","{}")); out={}
    for k,v in p.items():
        i=v["inputs"]; c=v["class_type"]
        if c=="KSampler": out.update({kk:i[kk] for kk in ("seed","steps","cfg","sampler_name","scheduler","denoise")})
        if c=="CheckpointLoaderSimple": out["ckpt"]=i["ckpt_name"]
        if c=="PrimitiveStringMultiline": out["prompt"]=i["value"]
        if c=="PrimitiveBoolean": out["use_reprompt"]=i["value"]
        if c=="PrimitiveFloat": out["duration"]=i["value"]
    return out
def analyse(path):
    x,sr,tags=load(path); m=x.mean(axis=1); n=len(m)
    win=int(0.01*sr); env=np.sqrt(np.convolve(m**2,np.ones(win)/win,'same')); db=20*np.log10(env+1e-9); top=db.max()
    r={"file":path,"dur":round(n/sr,3),"peak_dbfs":round(20*np.log10(np.abs(x).max()+1e-9),2),"clipped":int((np.abs(x)>=0.999).sum())}
    r["onset_s"]=round(np.argmax(db>top-40)/sr,3); r["loudest_s"]=round(np.argmax(env)/sr,3)
    r["levels"]={f"{t}s":round(float(db[min(n-1,int(t*sr))]-top),1) for t in (0.05,0.1,0.25,0.5,0.75,1.0,1.5,1.9) if t*sr<n}
    on=np.argmax(db>top-40); L=min(n-on,int(0.3*sr)); seg=m[on:on+L]*np.hanning(L)
    sp=np.abs(np.fft.rfft(seg))**2; f=np.fft.rfftfreq(L,1/sr); tot=sp.sum()
    r["spectrum_%"]={f"{a}-{b}":round(100*sp[(f>=a)&(f<b)].sum()/tot,1) for a,b in ((20,80),(80,200),(200,800),(800,3000),(3000,8000),(8000,20000))}
    # count separate peaks (>-6 dB, separated by >=0.15 s)
    pk=[]; i=0; hot=db>top-6
    while i<n:
        if hot[i]: pk.append(round(i/sr,2)); i+=int(0.15*sr)
        else: i+=1
    r["hits_above_-6dB"]=pk
    r["end_level_db"]=round(float(db[-int(0.05*sr):].mean()-top),1)
    r["settings"]=settings(tags)
    return r
if __name__=="__main__":
    for p in sys.argv[1:]: print(json.dumps(analyse(p),ensure_ascii=False,indent=1,default=float))
