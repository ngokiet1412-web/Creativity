#!/usr/bin/env python3
"""CAPY BK EP01 animatic, using the previously approved mascot GIF; no external assets.
Animated diagrams are explanatory sketches, not engineering drawings.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, os, subprocess, wave, json

OUT='/mnt/data'
GIF=os.path.join(OUT,'cheerful_capybara_workspace_celebration.png')
OUT_MP4=os.path.join(OUT,'CAPY_BK_EP01_animatic_demo.mp4')
OUT_COVER=os.path.join(OUT,'CAPY_BK_EP01_cover.jpg')
W,H,FPS=540,960,16
TOTAL=32
NAVY=(10,19,39); WHITE=(246,248,255); CYAN=(89,223,246); YELLOW=(255,199,70); RED=(254,97,102)
F_BOLD='/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf'
F_REG='/usr/share/fonts/truetype/noto/NotoSansDisplay-Regular.ttf'
fonts={}
def font(size,bold=False):
 k=(size,bold)
 if k not in fonts: fonts[k]=ImageFont.truetype(F_BOLD if bold else F_REG,size)
 return fonts[k]

def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def clamp(x,lo=0,hi=1):return max(lo,min(hi,x))
def lerp(a,b,u):return a+(b-a)*u

def centered(draw,txt,y,size=35,fill=WHITE,bold=True,stroke=0):
 f=font(size,bold); bb=draw.textbbox((0,0),txt,font=f,stroke_width=stroke)
 x=(W-(bb[2]-bb[0]))/2
 draw.text((x,y),txt,font=f,fill=fill,stroke_width=stroke,stroke_fill=(3,12,28))

def txt(draw,txt,xy,size=27,fill=WHITE,bold=False):draw.text(xy,txt,font=font(size,bold),fill=fill)

def rrect(draw,box,fill,r=14,outline=None,width=2): draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def grad_bg(top=(8,20,47),bottom=(19,47,80)):
 a=np.zeros((H,W,3),dtype=np.uint8)
 for y in range(H):
  u=y/(H-1)
  a[y,:,:]=[int(lerp(top[i],bottom[i],u)) for i in range(3)]
 return Image.fromarray(a,'RGB')
BG=grad_bg()
BG_WARM=grad_bg((29,34,53),(29,70,88))

im=Image.open(GIF)
FRAMES=[]
for i in range(im.n_frames):
 im.seek(i)
 FRAMES.append(im.convert('RGB').copy())
assert len(FRAMES)==9

# Studio footage preserved with its BK logo (background, polo and mug).
studio_bg=FRAMES[0].resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(26))
studio_bg=Image.blend(studio_bg,Image.new('RGB',(W,H),(4,12,31)),0.67)

def draw_header(draw, ep='TẬP 01', label='CAPY BK  •  KỸ THUẬT VUI'):
 rrect(draw,(24,27,W-24,76),(22,48,78),20,outline=(65,113,162),width=2)
 txt(draw,'🐻' if False else 'CAPY BK', (43,38),23,CYAN,True)
 txt(draw,ep,(W-118,40),20,YELLOW,True)

def draw_footer(draw, y=905):
 draw.line((30,y,W-30,y),fill=(75,118,159),width=2)
 centered(draw,'AI  •  Ô TÔ  •  MÁY CÔNG TRÌNH',y+15,17,(172,208,231),False)

def underline(draw,y,color=CYAN):draw.rounded_rectangle((W//2-57,y,W//2+57,y+6),3,fill=color)

def studio_scene(t,t0,caption,hero=None,subtitle=None):
 out=studio_bg.copy()
 d=ImageDraw.Draw(out)
 draw_header(d)
 # card of exact studio source, bob slightly
 dur=6
 idx=int(max(0,t-t0)*3.6)%len(FRAMES)
 fr=FRAMES[idx]
 zoom=1.0+.012*math.sin((t-t0)*2.1)
 fw=int(W*.98*zoom);fh=int(fw*fr.height/fr.width)
 src=fr.resize((fw,fh),Image.Resampling.LANCZOS)
 px=(W-fw)//2;py=218+int(4*math.sin((t-t0)*3.5))
 d.rounded_rectangle((9,py-9,W-9,py+fh+9),20,fill=(45,71,103))
 out.paste(src,(px,py))
 d=ImageDraw.Draw(out)
 if hero:
  centered(d,hero[0],110,39,YELLOW,True)
  centered(d,hero[1],156,45,WHITE,True)
 else:
  centered(d,'NCKH  ×  FUELGUARD',129,30,YELLOW,True)
 rrect(d,(23,690,W-23,854),(18,35,62),22,outline=(43,112,162),width=2)
 for j,line in enumerate(caption):
  centered(d,line,718+j*49,31,WHITE if j==0 else YELLOW,True)
 if subtitle:centered(d,868,0) if False else centered(d,subtitle,861,18,(185,218,235),False)
 draw_footer(d)
 return out

def excavator_scene(t,t0):
 u=(t-t0)
 out=BG_WARM.copy();d=ImageDraw.Draw(out)
 draw_header(d)
 centered(d,'MÁY XÚC LÊN DỐC',110,38,YELLOW)
 centered(d,'MỨC DẦU BÁO GIẢM?',165,33,WHITE)
 # background landscape
 d.ellipse((-150,210,400,760),fill=(25,70,94))
 d.polygon([(0,680),(W,495),(W,860),(0,860)],fill=(94,78,68))
 d.line((0,680,W,495),fill=(202,152,95),width=9)
 for j in range(14):
  x=(j*56+20)%W;y=676-int(x*185/W)+16
  d.ellipse((x,y,x+5,y+4),fill=(162,117,79))
 # excavator group drawn on transparent layer so we can tilt with ground
 layer=Image.new('RGBA',(440,380));ld=ImageDraw.Draw(layer)
 # track
 ld.rounded_rectangle((88,260,350,328),32,fill=(35,47,57),outline=(18,26,36),width=7)
 for x in range(117,333,44):ld.ellipse((x,270,x+41,311),fill=(105,126,131),outline=(11,25,35),width=5)
 ld.rounded_rectangle((116,201,324,276),21,fill=(245,167,28),outline=(111,82,35),width=5)
 ld.polygon([(134,116),(273,115),(313,210),(145,210)],fill=(253,192,48))
 ld.polygon([(165,135),(242,130),(261,197),(168,196)],fill=(66,156,187))
 ld.line((205,131,205,194),fill=(25,60,73),width=6)
 ld.ellipse((299,211,317,230),fill=(38,44,52))
 # moving boom
 a=math.sin(u*1.7)*6
 shoulder=(278,148); elbow=(363+int(a),81+int(a*.5)); tip=(400+int(a),134+int(a))
 ld.line((shoulder[0],shoulder[1],elbow[0],elbow[1]),fill=(121,76,17),width=27)
 ld.line((shoulder[0],shoulder[1],elbow[0],elbow[1]),fill=(247,172,38),width=20)
 ld.line((elbow[0],elbow[1],tip[0],tip[1]),fill=(121,76,17),width=21)
 ld.line((elbow[0],elbow[1],tip[0],tip[1]),fill=(251,190,44),width=15)
 ld.polygon([(tip[0]-10,tip[1]),(tip[0]+31,tip[1]+9),(tip[0]+9,tip[1]+41)],fill=(85,90,92))
 ld.text((145,228),'BK',font=font(24,True),fill=(23,80,112))
 # rot  - slope a visual tilt
 layer=layer.rotate(17,expand=True,resample=Image.Resampling.BICUBIC)
 X=62+int(6*math.sin(u*2));Y=383+int(3*math.cos(u*3));out.paste(layer,(X,Y),layer)
 d=ImageDraw.Draw(out)
 # round level counter
 rrect(d,(43,745,W-43,864),(18,36,62),18,outline=(62,105,137),width=2)
 txt(d,'MỨC DẦU HIỂN THỊ', (62,764),21,(191,217,237),True)
 val=round(76-12*ease((u-.6)/3.0))
 txt(d,f'{val}%', (63,797),49,YELLOW,True)
 d.rounded_rectangle((223,811,465,830),9,fill=(60,82,98))
 d.rounded_rectangle((223,811,223+int(242*val/100),830),9,fill=CYAN)
 if u>3.6:
  rrect(d,(88,660,452,716),(101,38,48),12)
  centered(d,'CHƯA THỂ KẾT LUẬN!',671,25,WHITE)
 draw_footer(d)
 return out

def clip_halfplane(points,cut):
 # keep y>=cut. Screen y downward.
 ret=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)]
  a=P[1]>=cut;b=Q[1]>=cut
  if a:ret.append(P)
  if a!=b:
   r=(cut-P[1])/(Q[1]-P[1]);ret.append((P[0]+r*(Q[0]-P[0]),cut))
 return ret

def fuel_scene(t,t0):
 u=t-t0
 out=BG.copy();d=ImageDraw.Draw(out)
 draw_header(d)
 centered(d,'VẬY DẦU ĐI ĐÂU?',112,40,YELLOW)
 centered(d,'KHÔNG HỀ BIẾN MẤT!',163,30,WHITE)
 # tank diagram frame
 rrect(d,(24,246,W-24,715),(19,45,76),24,outline=(66,128,164),width=2)
 d.rounded_rectangle((47,265,493,309),15,fill=(33,68,97))
 centered(d,'MÔ PHỎNG NGUYÊN LÝ',269,20,CYAN,True)
 cx,cy=270,506
 ang=math.radians(lerp(0,19,ease((u-1.2)/3.8)) + math.sin(u*2)*1.5)
 coords=[(-175,-96),(175,-96),(175,96),(-175,96)]
 pts=[]
 for x,y in coords:
  pts.append((cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang)))
 level=cy+14 # absolute horizontal fuel surface in the world
 mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
 inside=clip_halfplane(pts,level)
 if len(inside)>=3:md.polygon(inside,fill=255)
 # add a blue fluid fill graphic clipped to tank
 li=Image.new('RGB',(W,H),(47,168,227));out.paste(li,(0,0),mask)
 d=ImageDraw.Draw(out)
 d.polygon(pts,outline=(202,229,244),width=9)
 d.line((cx-225,level,cx+225,level),fill=(116,227,253),width=4)
 # sensor at local x=-116, tube follows tank
 x=-122;top_local=-77;bot_local=80
 def transform(xx,yy):return (cx+xx*math.cos(ang)-yy*math.sin(ang),cy+xx*math.sin(ang)+yy*math.cos(ang))
 top=transform(x,top_local);bot=transform(x,bot_local)
 d.line((top[0],top[1],bot[0],bot[1]),fill=(255,201,80),width=8)
 # fake float at intersection world y=level
 fraction=clamp((level-top[1])/(bot[1]-top[1])) if abs(bot[1]-top[1])>1 else .5
 fx=lerp(top[0],bot[0],fraction);fy=lerp(top[1],bot[1],fraction)
 d.ellipse((fx-15,fy-15,fx+15,fy+15),fill=YELLOW,outline=(31,49,65),width=4)
 txt(d,'PHAO', (76,639),21,YELLOW,True)
 d.line((130,646,fx-16,fy+12),fill=YELLOW,width=3)
 # angle indicator below
 txt(d,'Góc nghiêng bình:', (47,738),24,(202,222,237))
 txt(d,f'{int(math.degrees(ang))}°', (375,734),31,YELLOW,True)
 txt(d,'Mặt thoáng giữ phương ngang', (47,794),23,CYAN,True)
 txt(d,'Vị trí phao có thể thay đổi', (47,830),21,WHITE)
 draw_footer(d)
 return out

def sensors_scene(t,t0):
 u=t-t0
 out=BG.copy();d=ImageDraw.Draw(out)
 draw_header(d)
 centered(d,'MUỐN PHÁT HIỆN',115,40,YELLOW)
 centered(d,'DẤU HIỆU MẤT DẦU?',168,33,WHITE)
 cards=[('MỨC NHIÊN LIỆU','Cảm biến', (49,290,491,388)),('ĐỘ NGHIÊNG / RUNG','IMU',(49,417,491,515)),('TRẠNG THÁI MÁY','Dữ liệu vận hành',(49,544,491,642))]
 for k,(name,caption,bbox) in enumerate(cards):
  p=ease((u-k*.65-.1)/.65)
  if p<=0:continue
  left=bbox[0]+int((1-p)*470)
  b=(left,bbox[1],left+442,bbox[3])
  rrect(d,b,(22,61,96),20,outline=(68,143,184),width=2)
  d.ellipse((left+17,bbox[1]+24,left+56,bbox[1]+63),fill=CYAN if k<2 else YELLOW)
  txt(d,name,(left+69,bbox[1]+13),25,WHITE,True)
  txt(d,caption,(left+69,bbox[1]+53),17,(176,210,231))
  if p>.95:d.line((W//2,bbox[3],W//2,bbox[3]+16),fill=CYAN,width=4)
 if u>2.5:
  yy=725+int(5*math.sin(u*4))
  rrect(d,(40,yy,W-40,yy+91),(29,103,116),21,outline=CYAN,width=3)
  centered(d,'PHÂN TÍCH BẤT THƯỜNG',yy+19,27,WHITE)
 txt(d,'FuelGuard • hướng nghiên cứu', (79,854),19,(172,204,220))
 draw_footer(d)
 return out

def ending_scene(t,t0):
 u=t-t0
 out=studio_scene(t,t0,['ĐO ĐÚNG TRƯỚC KHI','KẾT LUẬN!'],hero=['KHÔNG PHẢI CỨ TỤT DẦU','LÀ BỊ TRỘM!'])
 d=ImageDraw.Draw(out)
 if u>2.0:
  k=ease((u-2)/.4)
  rrect(d,(41,621,499,671),(47,106,114),15)
  centered(d,'TẬP SAU: MÁY XÚC BIẾT NÓI?',632,22,WHITE)
 return out

segments=[(0,5,'studio'),(5,11,'excavator'),(11,20,'fuel'),(20,26,'sensors'),(26,TOTAL,'ending')]

def render(t):
 if t<5:return studio_scene(t,0,['CAPY: DẦU TỤT RỒI!','BỊ RÚT TRỘM HẢ?!'],hero=['MÁY XÚC','BỊ RÚT TRỘM DẦU?'])
 if t<11:return excavator_scene(t,5)
 if t<20:return fuel_scene(t,11)
 if t<26:return sensors_scene(t,20)
 return ending_scene(t,26)

print('Rendering video',W,H,FPS,TOTAL,flush=True)
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=44100', '-map','0:v','-c:v','libx264','-crf','20','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart','-t',str(TOTAL),'-an',os.path.join(OUT,'_capy_bk_ep01_silent.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for i in range(TOTAL*FPS):
 frame=render(i/FPS)
 if i==2*FPS:frame.save(OUT_COVER,quality=92)
 try:proc.stdin.write(frame.tobytes())
 except BrokenPipeError:
  print(proc.stderr.read().decode());raise
 if i%(FPS*5)==0: print('frames',i,'/',TOTAL*FPS,flush=True)
proc.stdin.close();err=proc.stderr.read();rc=proc.wait()
if rc!=0:raise RuntimeError(err.decode())
# compose custom royalty-free sound motif (not voiceover)
sr=44100;n=int(sr*TOTAL);audio=np.zeros(n,dtype=np.float32)
def tone(start,dur,hz,amp=.12,kind='pluck'):
 i0=max(0,int(start*sr)); nn=min(n-i0,int(dur*sr));
 if nn<=0:return
 tt=np.arange(nn)/sr
 env=np.exp(-5*tt/max(dur,1e-5))*(1-np.exp(-100*tt))
 s=np.sin(2*np.pi*hz*tt)+.3*np.sin(4*np.pi*hz*tt)
 audio[i0:i0+nn]+=amp*env*s
# 4-note capy theme, sparse bell beat
for ts in np.arange(0,TOTAL,4):
 for j,freq in enumerate([392,494,587,784]):tone(float(ts+j*.31),.52,freq,.095)
for ts in np.arange(.0,TOTAL,.5):
 # quiet rhythmic tick + handclap
 tone(float(ts),.095,110,.035)
for ts in [0,5,11,20,26]:
 tone(ts,.37,880,.13);tone(ts+.11,.45,1175,.08)
# ending jingle
for j,fr in enumerate([523,659,784,1047]):tone(29.7+j*.32,.7,fr,.10)
audio=np.tanh(audio*1.05)*.65
raw_audio=os.path.join(OUT,'_capy_bk_music.wav')
with wave.open(raw_audio,'wb') as wf:
 wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr);wf.writeframes((audio*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',os.path.join(OUT,'_capy_bk_ep01_silent.mp4'),'-i',raw_audio,'-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',OUT_MP4],check=True)
print('DONE',OUT_MP4,os.path.getsize(OUT_MP4),'bytes',flush=True)
# shot and dialogue contract for Codex / a later AI voice pass
meta={
 'title':'CAPY BK — EP01: Máy xúc bị rút trộm dầu?',
 'aspect_ratio':'9:16','resolution':f'{W}x{H}','fps':FPS,'duration_seconds':TOTAL,
 'status':'animatic with synthetic original sound bed, no narration/lipsync',
 'source_mascot_file':'cheerful_capybara_workspace_celebration.png (GIF despite PNG filename)',
 'segments':[
 {'start':0,'end':5,'type':'studio','narration':'Ê ê, máy xúc bị tụt dầu rồi! Bị rút trộm hả?'},
 {'start':5,'end':11,'type':'excavator','narration':'Khoan! Máy lên dốc, cảm biến có thể báo khác.'},
 {'start':11,'end':20,'type':'technical schematic','narration':'Khi bình nghiêng, mặt thoáng nhiên liệu thay đổi so với bình. Vị trí phao có thể thay đổi, dù nhiên liệu chưa thực sự bị rút.'},
 {'start':20,'end':26,'type':'signals','narration':'Đó là lý do cần kết hợp mức nhiên liệu, độ nghiêng và trạng thái vận hành, rồi mới đánh giá bất thường.'},
 {'start':26,'end':32,'type':'studio closing','narration':'Nhớ nha! Phải đo đúng rồi mới kết luận. Tập sau cho máy xúc biết nói!'}],
 'technical_caution':'Illustrations are conceptual; not specific to a real Komatsu tank/sensor; FuelGuard detection not independently validated.'}
with open(os.path.join(OUT,'CAPY_BK_EP01_animatic_shotlist.json'),'w',encoding='utf-8') as f:json.dump(meta,f,ensure_ascii=False,indent=2)
