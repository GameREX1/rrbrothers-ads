#!/usr/bin/env python3
"""Create a cinematic RR Brothers online-store advertisement (vertical Shorts)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import imageio_ffmpeg
import wave, subprocess, os, math, random

W, H, FPS = 1080, 1920, 30
SCENE_SECONDS, XFADE = 3.8, 0.45
PRODUCT_FILE = "WhatsApp Image 2026-10-28 at 8.05.08 AM.jpeg"
LOGO_FILE = "RR Brothers Neon Metallic Emblem.jpg"
OUTPUT = "RR-Brothers-Website-Ad.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
GOLD = (225, 190, 121)
CREAM = (247, 243, 235)
MUTED = (179, 171, 158)

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def spaced(draw, text, y, fnt, color, spacing=0, center=W/2):
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * max(0, len(text)-1)
    x = center - total/2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=color)
        x += cw + spacing

def centered(draw, text, y, size, color=CREAM, bold=False, spacing=0):
    spaced(draw, text, y, font(size, bold), color, spacing)

def background(seed=1):
    yy, xx = np.mgrid[0:H, 0:W]
    nx = (xx - W*0.52)/(W*.72)
    ny = (yy - H*.40)/(H*.62)
    glow = np.clip(1-np.sqrt(nx*nx + ny*ny), 0, 1)
    vertical = (yy/H)*5
    arr = np.zeros((H,W,3), dtype=np.float32)
    arr[:,:,0] = 7 + vertical + glow*20
    arr[:,:,1] = 7 + vertical*.8 + glow*15
    arr[:,:,2] = 8 + vertical*.4 + glow*8
    rng = np.random.default_rng(seed)
    grain = rng.normal(0, .65, (H,W,1))
    arr += grain
    im = Image.fromarray(np.uint8(np.clip(arr,0,255)), "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((46,46,W-46,H-46), outline=(225,190,121,90), width=2)
    d.rectangle((46,46,185,51), fill=(225,190,121,210))
    d.rectangle((W-185,H-51,W-46,H-46), fill=(225,190,121,210))
    for i in range(55):
        x = int(rng.integers(70,W-70)); y = int(rng.integers(80,H-80))
        r = int(rng.integers(1,4))
        d.ellipse((x-r,y-r,x+r,y+r), fill=(235,203,145,int(rng.integers(18,65))))
    # Fine light streaks along the top and lower edge
    d.line((90,270,990,270), fill=(225,190,121,35), width=2)
    d.line((90,1650,990,1650), fill=(225,190,121,28), width=2)
    return im

def fit_inside(source, size, bg=(239,235,226), padding=22):
    w,h = size
    source = source.convert("RGB").copy()
    source.thumbnail((w-padding*2,h-padding*2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB",(w,h),bg)
    canvas.paste(source,((w-source.width)//2,(h-source.height)//2))
    return canvas

def add_card(base, card, xy, radius=30, border=(225,190,121,150), blur=26):
    x,y = xy
    shadow = Image.new("RGBA",(card.width+100,card.height+100),(0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((38,38,card.width+62,card.height+62),radius=radius+8,fill=(0,0,0,185))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    base.paste(shadow,(x-50,y-40),shadow)
    mask = Image.new("L",card.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,card.width-1,card.height-1),radius=radius,fill=255)
    base.paste(card,(x,y),mask)
    if border:
        ImageDraw.Draw(base).rounded_rectangle((x,y,x+card.width-1,y+card.height-1),radius=radius,outline=border,width=2)

def pill(draw, box, text, fill=(225,190,121,255), textfill=(15,13,10,255), size=22):
    draw.rounded_rectangle(box,radius=(box[3]-box[1])//2,fill=fill)
    f=font(size,True)
    draw.text(((box[0]+box[2])/2,(box[1]+box[3])/2),text,font=f,fill=textfill,anchor="mm")

def scene_hook():
    im=background(11); d=ImageDraw.Draw(im,"RGBA")
    centered(d,"RR BROTHERS",360,31,GOLD,True,7)
    centered(d,"YOUR STYLE.",650,95,CREAM,True,1)
    centered(d,"YOUR STORE.",770,100,GOLD,True,1)
    d.rounded_rectangle((W/2-95,925,W/2+95,932),radius=3,fill=GOLD)
    centered(d,"DISCOVER YOUR NEXT FAVOURITE",1015,25,MUTED,True,4)
    centered(d,"SHOP ONLINE",1450,31,CREAM,True,8)
    return im

def scene_product(product):
    im=background(22); d=ImageDraw.Draw(im,"RGBA")
    centered(d,"FIND YOUR NEXT FAVOURITE",175,28,GOLD,True,6)
    centered(d,"A FRESH PICK.",270,61,CREAM,True,1)
    card=fit_inside(product,(850,1080),(244,241,234),24)
    add_card(im,card,(115,450),32,(225,190,121,190))
    centered(d,"CURATED FOR YOUR EVERYDAY",1610,22,MUTED,True,4)
    centered(d,"EXPLORE THE COLLECTION",1680,28,CREAM,True,5)
    return im

def draw_phone(draw, product, logo):
    # Phone shell
    x1,y1,x2,y2 = 155,235,925,1575
    draw.rounded_rectangle((x1,y1,x2,y2),radius=82,fill=(8,8,9,255),outline=(212,184,125,220),width=5)
    draw.rounded_rectangle((x1+18,y1+18,x2-18,y2-18),radius=66,fill=(16,16,17,255))
    draw.rounded_rectangle((445,260,635,286),radius=13,fill=(47,47,48,255))
    # Site navigation
    draw.text((220,340),"RR BROTHERS",font=font(35,True),fill=GOLD)
    draw.text((220,392),"ONLINE STORE",font=font(15,True),fill=MUTED)
    draw.rounded_rectangle((215,455,865,535),radius=22,fill=(35,35,36,255),outline=(75,69,59,255),width=2)
    draw.text((250,477),"Search the collection",font=font(21),fill=(174,169,160,255))
    draw.text((790,477),"⌕",font=font(42,True),fill=GOLD)
    # Product card within mobile layout
    p=fit_inside(product,(590,650),(240,237,229),20)
    mask=Image.new("L",p.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,p.width-1,p.height-1),radius=22,fill=255)
    im=Image.new("RGBA",(p.width,p.height),(0,0,0,0)); im.paste(p,(0,0)); 
    # Product photo is a real uploaded asset, placed in an illustrated storefront panel.
    draw.rounded_rectangle((215,570,865,1240),radius=26,fill=(239,236,228,255),outline=(225,190,121,190),width=2)
    draw.text((252,1270),"EXPLORE NEW ARRIVALS",font=font(24,True),fill=CREAM)
    draw.text((252,1320),"Find something you love.",font=font(20),fill=MUTED)
    pill(draw,(250,1400,830,1480),"SHOP THE COLLECTION",size=21)

def scene_phone(product):
    im=background(33)
    d=ImageDraw.Draw(im,"RGBA")
    centered(d,"A STORE THAT MOVES WITH YOU",135,24,GOLD,True,4)
    # create phone artwork to a transparent overlay then place photo in UI
    phone_layer=Image.new("RGBA",(W,H),(0,0,0,0))
    pd=ImageDraw.Draw(phone_layer,"RGBA")
    x1,y1,x2,y2=155,235,925,1575
    pd.rounded_rectangle((x1,y1,x2,y2),radius=82,fill=(7,7,8,255),outline=(212,184,125,230),width=5)
    pd.rounded_rectangle((x1+18,y1+18,x2-18,y2-18),radius=66,fill=(16,16,17,255))
    pd.rounded_rectangle((445,260,635,286),radius=13,fill=(47,47,48,255))
    pd.text((220,340),"RR BROTHERS",font=font(35,True),fill=GOLD)
    pd.text((220,392),"ONLINE STORE",font=font(15,True),fill=MUTED)
    pd.rounded_rectangle((215,455,865,535),radius=22,fill=(35,35,36,255),outline=(75,69,59,255),width=2)
    pd.text((250,477),"Search the collection",font=font(21),fill=(174,169,160,255))
    pd.text((790,477),"⌕",font=font(42,True),fill=GOLD)
    pd.rounded_rectangle((215,570,865,1240),radius=26,fill=(239,236,228,255),outline=(225,190,121,190),width=2)
    p=fit_inside(product,(590,600),(239,236,228),18)
    mask=Image.new("L",p.size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,p.width-1,p.height-1),radius=20,fill=255)
    phone_layer.paste(p,(245,605),mask)
    pd.text((252,1270),"EXPLORE NEW ARRIVALS",font=font(24,True),fill=CREAM)
    pd.text((252,1320),"Find something you love.",font=font(20),fill=MUTED)
    pill(pd,(250,1400,830,1480),"SHOP THE COLLECTION",size=21)
    im.alpha_composite(phone_layer) if im.mode=="RGBA" else im.paste(phone_layer,(0,0),phone_layer)
    centered(d,"YOUR FAVOURITES. JUST A FEW TAPS AWAY.",1665,19,MUTED,True,3)
    return im

def scene_steps():
    im=background(44); d=ImageDraw.Draw(im,"RGBA")
    centered(d,"ONLINE SHOPPING.",280,58,CREAM,True,2)
    centered(d,"MADE SIMPLE.",365,68,GOLD,True,2)
    labels=[("01","BROWSE","Explore the collection"),("02","CHOOSE","Pick your favourite"),("03","ORDER","Shop online with ease")]
    y=600
    for number,title,sub in labels:
        d.rounded_rectangle((115,y,965,y+245),radius=28,fill=(20,19,17,215),outline=(225,190,121,105),width=2)
        d.text((165,y+48),number,font=font(49,True),fill=GOLD)
        d.text((335,y+43),title,font=font(40,True),fill=CREAM)
        d.text((335,y+112),sub,font=font(22),fill=MUTED)
        d.rounded_rectangle((840,y+80,900,y+140),radius=25,outline=(225,190,121,160),width=3)
        d.line((858,y+110,873,y+125),fill=GOLD,width=4)
        d.line((873,y+125,887,y+94),fill=GOLD,width=4)
        y+=285
    centered(d,"START EXPLORING TODAY",1515,26,GOLD,True,5)
    return im

def scene_cta(product):
    im=background(55); d=ImageDraw.Draw(im,"RGBA")
    card=fit_inside(product,(690,690),(242,239,231),16)
    add_card(im,card,(195,265),26,(225,190,121,190))
    centered(d,"MAKE ROOM FOR",1110,47,CREAM,True,2)
    centered(d,"SOMETHING NEW.",1185,66,GOLD,True,1)
    centered(d,"DISCOVER RR BROTHERS ONLINE",1350,24,MUTED,True,4)
    pill(d,(180,1455,900,1540),"VISIT RRBROTHER.SITE",size=29)
    return im

def scene_end(logo):
    im=background(66); d=ImageDraw.Draw(im,"RGBA")
    panel=Image.new("RGB",(720,720),(9,9,10))
    lg=logo.convert("RGB").copy()
    lg.thumbnail((690,690),Image.Resampling.LANCZOS)
    panel.paste(lg,((720-lg.width)//2,(720-lg.height)//2))
    add_card(im,panel,(180,320),34,(225,190,121,180))
    centered(d,"RR BROTHERS",1165,64,GOLD,True,8)
    centered(d,"YOUR ONLINE STORE",1260,28,CREAM,True,6)
    d.rounded_rectangle((W/2-100,1340,W/2+100,1347),radius=3,fill=GOLD)
    centered(d,"SHOP NOW",1410,40,CREAM,True,8)
    centered(d,"rrbrother.site",1505,29,MUTED,False,3)
    return im

def create_audio(path, duration):
    sr=44100
    n=int(sr*duration)
    t=np.arange(n,dtype=np.float32)/sr
    rng=np.random.default_rng(987)
    mix=np.zeros(n,dtype=np.float32)
    chords=[
        [110.00,146.83,174.61,220.00],
        [98.00,130.81,164.81,196.00],
        [116.54,146.83,174.61,233.08],
        [87.31,130.81,164.81,220.00],
    ]
    bar=duration/4
    for i,notes in enumerate(chords):
        s=int(i*bar*sr); e=min(n,int((i+1)*bar*sr))
        tt=t[s:e]-i*bar
        env=np.minimum(1,tt/.7)*np.minimum(1,(bar-tt)/.8)
        for j,f in enumerate(notes):
            mix[s:e] += (0.026/(j+1))*np.sin(2*np.pi*f*tt+j*.2)*env
            mix[s:e] += (0.007/(j+1))*np.sin(2*np.pi*(f*2.003)*tt)*env
    # A soft low beat and short airy accents give the film a deliberate rhythm.
    for sec in np.arange(.2,duration,1.25):
        s=int(sec*sr); length=min(int(.34*sr),n-s)
        if length<=0: continue
        tt=np.arange(length,dtype=np.float32)/sr
        env=np.exp(-tt*12)
        mix[s:s+length] += .045*np.sin(2*np.pi*(68-20*tt)*tt)*env
    for sec,freq in [(3.2,523.25),(6.5,659.25),(9.8,587.33),(13.1,698.46),(16.4,783.99)]:
        s=int(sec*sr); length=min(int(.9*sr),n-s)
        if length<=0: continue
        tt=np.arange(length,dtype=np.float32)/sr
        mix[s:s+length] += .032*np.sin(2*np.pi*freq*tt)*np.exp(-tt*3.5)
    fade=int(.9*sr)
    mix[:fade]*=np.linspace(0,1,fade)
    mix[-fade:]*=np.linspace(1,0,fade)
    mix=np.clip(mix,-.2,.2)
    stereo=np.stack([mix,mix],axis=1)
    with wave.open(path,"wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((stereo*32767).astype("<i2").tobytes())

def main():
    if not os.path.isfile(PRODUCT_FILE) or not os.path.isfile(LOGO_FILE):
        raise FileNotFoundError("The repository must contain the uploaded product image and RR Brothers logo.")
    product=Image.open(PRODUCT_FILE)
    logo=Image.open(LOGO_FILE)
    scenes=[
        scene_hook(),
        scene_product(product),
        scene_phone(product),
        scene_steps(),
        scene_cta(product),
        scene_end(logo),
    ]
    for i,scene in enumerate(scenes,1):
        scene.save(f"website-scene-{i}.png",optimize=True)
    duration=len(scenes)*SCENE_SECONDS-(len(scenes)-1)*XFADE
    create_audio("website-ambient.wav",duration)
    for i in range(1,len(scenes)+1):
        zoom = "min(1.075,1+0.00045*on)"
        xexpr = "iw/2-(iw/zoom/2)" if i%2 else "iw/2-(iw/zoom/2)+16*on"
        yexpr = "ih/2-(ih/zoom/2)"
        cmd=[
            FFMPEG,"-y","-hide_banner","-loglevel","error",
            "-loop","1","-framerate",str(FPS),"-i",f"website-scene-{i}.png",
            "-t",str(SCENE_SECONDS),
            "-vf",f"zoompan=z='{zoom}':x='{xexpr}':y='{yexpr}':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
            "-an","-c:v","libx264","-preset","veryfast","-crf","18",
            f"website-segment-{i}.mp4"
        ]
        subprocess.run(cmd,check=True)
    args=[]
    for i in range(len(scenes)):
        args += ["-i",f"website-segment-{i+1}.mp4"]
    # 6 scenes with 0.45 second overlaps.
    filter_parts=[]
    previous="[0:v]"
    for idx in range(1,len(scenes)):
        out=f"[v{idx}]"
        offset=idx*(SCENE_SECONDS-XFADE)
        filter_parts.append(f"{previous}[{idx}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.2f}{out}")
        previous=out
    filter_parts.append(f"{previous}format=yuv420p[v]")
    fc=";".join(filter_parts)
    subprocess.run([
        FFMPEG,"-y","-hide_banner","-loglevel","error",*args,
        "-filter_complex",fc,"-map","[v]","-r",str(FPS),
        "-c:v","libx264","-preset","medium","-crf","18",
        "-pix_fmt","yuv420p","-movflags","+faststart","website-silent.mp4"
    ],check=True)
    subprocess.run([
        FFMPEG,"-y","-hide_banner","-loglevel","error",
        "-i","website-silent.mp4","-i","website-ambient.wav",
        "-map","0:v:0","-map","1:a:0","-c:v","copy",
        "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",OUTPUT
    ],check=True)
    print(f"Created {OUTPUT}: {duration:.2f}s, {W}x{H}, {FPS}fps")

if __name__=="__main__":
    main()
