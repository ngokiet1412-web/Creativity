"""Frame-difference stillness check (owner method: t vs t+0.25 s every 0.5 s, 320x180 gray)."""
import subprocess, numpy as np, sys
f=sys.argv[1]
W,H=320,180
raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf',f'scale={W}:{H},format=gray','-f','rawvideo','-'],capture_output=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(np.float32)
n=len(fr); print('frames',n)
# owner's method: t vs t+0.25 every 0.5 s
low=[];tot=0
for t in np.arange(0,n/30-0.25,0.5):
    a=fr[int(round(t*30))]; b=fr[int(round((t+0.25)*30))]; d=np.abs(a-b).mean(); tot+=1
    if d<0.5: low.append(round(t,2))
print('owner-method samples',tot,'below 0.5/255:',len(low),low)
# longest run of near-identical consecutive frames
diff=np.abs(np.diff(fr,axis=0)).mean(axis=(1,2))
run=0;best=(0,0);start=0
for i,d in enumerate(diff):
    if d<0.08:
        if run==0: start=i
        run+=1
        if run>best[0]: best=(run,start)
    else: run=0
print('longest still run %.2fs starting %.2fs'%(best[0]/30,best[1]/30))
# per-second motion
for s in range(int(n/30)):
    seg=diff[s*30:(s+1)*30]
    print(s, round(float(seg.mean()),3), end=' | ')
print()
