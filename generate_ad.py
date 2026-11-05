#!/usr/bin/env python3
"""Render a vertical RR Brothers product advertisement from the repository images."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import imageio_ffmpeg
import wave, subprocess, os, math, random

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1080, 1920
FPS = 30
SCENE_SECONDS = 3.8
XFADE = 0.55
PRODUCT = "WhatsApp Image 2026-10-28 at 8.05.08 AM.jpeg"
LOGO = "RR Brothers Neon Metallic Emblem.jpg"
OUT = "RR-Brothers-Shorts.mp4"
GOLD = (222, 186, 112)
IVORY = (247, 242, 232)
MUTED = (194, 184, 166)

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for f in candidates:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def centered(draw, text, y, fnt, fill, spacing=0):
    if spacing:
        widths = [draw.textlength(c, font=fnt) for c in text]
        total = sum(widths) + spacing * (len(text)-1)
        x = (W-total)/2
        for c, cw in zip(text, widths):
            draw.text((x,y), c, font=fnt, fill=fill)
            x += cw + spacing
    else:
        draw.text((W/2,y), text, font=fnt, fill=fill, anchor="mt")

def make_bg(seed):
    im = Image.new("RGB", (W,H))
    px = im.load()
    random.seed(seed)
    # black-to-warm-charcoal gradient with a soft amber center glow
    for y in range(H):
        for x in range(W):
            dx=(x-W*0.52)/(W*0.72); dy=(y-H*0.40)/(H*0.62)
            glow=max(0,1-math.sqrt(dx*dx+dy*dy))
            v=int(8+glow*15)
            px[x,y]=(v+int(glow*8), v+int(glow*6), v+int(glow*2))
    d=ImageDraw.Draw(im, "RGBA")
    d.rectangle((42,42,W-42,H-42), outline=(220,184,111,85), width=2)
    d.rectangle((42,42,175,47), fill=(222,186,112,190))
    d.rectangle((W-175,H-47,W-42,H-42), fill=(222,186,112,190))
    # subtle dust bokeh
    for _ in range(55):
        x=random.randint(65,W-65); y=random.randint(80,H-80); r=random.choice([1,2,3])
        d.ellipse((x-r,y-r,x+r,y+r), fill=(229,194,126,random.randint(20,65)))
    return im

def fit_inside(source, size, background=(244,239,229)):
    w,h=size
    im=Image.new("RGB",(w,h),background)
    src=source.convert("RGB").copy()
    src.thumbnail((w-30,h-30), Image.Resampling.LANCZOS)
    im.paste(src,((w-src.width)//2,(h-src.height)//2))
    return im

def add_card(base, card, xy, radius=26):
    x,y=xy
    shadow=Image.new("RGBA",(card.width+80,card.height+80),(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((30,30,card.width+50,card.height+50),radius=radius+8,fill=(0,0,0,180))
    shadow=shadow.filter(ImageFilter.GaussianBlur(24))
    base.paste(shadow,(x-40,y-25),shadow)
    mask=Image.new("L",card.size,0); md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,card.width-1,card.height-1),radius=radius,fill=255)
    base.paste(card,(x,y),mask)

def scene_open():
    im=make_bg(1); d=ImageDraw.Draw(im)
    centered(d,"RR BROTHERS",445,font(34,True),GOLD,7)
    centered(d,"THE EVERYDAY",755,font(76,True),IVORY,1)
    centered(d,"STYLE EDIT",855,font(112,True),GOLD,2)
    d.rounded_rectangle((W//2-95,1010,W//2+95,1016),radius=3,fill=GOLD)
    centered(d,"A NEW PICK FOR YOUR WARDROBE",1080,font(23),MUTED,4)
    centered(d,"OWN YOUR EVERYDAY",1585,font(22,True),IVORY,5)
    return im

def scene_product(product, variant):
    im=make_bg(variant+2); d=ImageDraw.Draw(im)
    centered(d,"NEW ARRIVAL",165,font(34,True),GOLD,8)
    centered(d,"YOUR NEXT",245,font(55,True),IVORY,2)
    centered(d,"FAVOURITE LOOK.",312,font(62,True),GOLD,1)
    card=fit_inside(product,(800,990))
    add_card(im,card,(140,465),28)
    centered(d,"RR BROTHERS COLLECTION",1530,font(25,True),IVORY,5)
    centered(d,"MADE TO MOVE WITH YOUR DAY",1590,font(20),MUTED,3)
    return im

def scene_sizes(product):
    im=make_bg(5); d=ImageDraw.Draw(im)
    centered(d,"THE LOOK",160,font(44,True),GOLD,7)
    centered(d,"THAT FEELS RIGHT.",238,font(58,True),IVORY,1)
    card=fit_inside(product,(600,760))
    add_card(im,card,(240,390),24)
    d.rounded_rectangle((125,1225,955,1470),radius=28,outline=(222,186,112,155),width=3,fill=(15,14,12,210))
    centered(d,"AVAILABLE SIZES",1280,font(23,True),MUTED,6)
    centered(d,"S    /    M    /    L",1350,font(57,True),IVORY,3)
    centered(d,"YOUR SIZE. YOUR STYLE.",1550,font(22),GOLD,5)
    return im

def scene_price():
    im=make_bg(6); d=ImageDraw.Draw(im)
    centered(d,"A FRESH LOOK",410,font(50,True),IVORY,4)
    centered(d,"FOR JUST",495,font(34),MUTED,7)
    centered(d,"Rs. 2,000",660,font(112,True),GOLD,2)
    d.rounded_rectangle((180,855,900,860),radius=2,fill=(222,186,112,200))
    centered(d,"AVAILABLE NOW",945,font(31,True),IVORY,7)
    centered(d,"S  /  M  /  L",1040,font(43,True),MUTED,5)
    centered(d,"RR BROTHERS",1470,font(46,True),GOLD,7)
    return im

def scene_outro(logo):
    im=make_bg(7); d=ImageDraw.Draw(im)
    lg=logo.convert("RGB").copy()
    lg.thumbnail((620,620),Image.Resampling.LANCZOS)
    # Logo placed on clean dark canvas, keeping the original mark intact
    panel=Image.new("RGB",(760,760),(10,10,10))
    panel.paste(lg,((760-lg.width)//2,(760-lg.height)//2))
    add_card(im,panel,(160,330),24)
    centered(d,"RR BROTHERS",1195,font(62,True),GOLD,8)
    centered(d,"OWN YOUR EVERYDAY",1290,font(26,True),IVORY,6)
    d.rounded_rectangle((W//2-90,1360,W//2+90,1366),radius=3,fill=GOLD)
    centered(d,"SHOP NOW",1435,font(38,True),IVORY,7)
    centered(d,"rrbrother.site",1515,font(27),MUTED,4)
    return im

def make_audio(path, duration):
    sr=44100
    n=int(sr*duration)
    t=np.arange(n,dtype=np.float32)/sr
    # Original, soft cinematic ambient bed (no sampled or copyrighted music).
    chords=[
        [130.81,164.81,196.00,261.63],
        [98.00,146.83,196.00,246.94],
        [110.00,164.81,220.00,261.63],
        [87.31,130.81,174.61,220.00],
    ]
    mix=np.zeros(n,dtype=np.float32)
    chord_len=duration/4
    for ci,notes in enumerate(chords):
        start=int(ci*chord_len*sr); end=min(n,int((ci+1)*chord_len*sr))
        tt=t[start:end]-ci*chord_len
        env=np.minimum(1,tt/0.7)*np.minimum(1,(chord_len-tt)/0.9)
        for j,f in enumerate(notes):
            mix[start:end] += (0.028/(j+1))*np.sin(2*np.pi*f*tt + j*.18)*env
            mix[start:end] += (0.009/(j+1))*np.sin(2*np.pi*(f*1.002)*tt)*env
    # A few gentle high chimes at scene changes
    for sec,f in [(3.25,523.25),(6.5,659.25),(9.75,587.33),(13,783.99)]:
        st=int(sec*sr); length=min(int(.85*sr),n-st)
        if length>0:
            tt=np.arange(length)/sr
            env=np.exp(-tt*3.3)
            mix[st:st+length] += .045*np.sin(2*np.pi*f*tt)*env
    fade=int(.9*sr)
    mix[:fade] *= np.linspace(0,1,fade)
    mix[-fade:] *= np.linspace(1,0,fade)
    mix=np.clip(mix,-.22,.22)
    stereo=np.stack([mix,mix],axis=1)
    pcm=(stereo*32767).astype("<i2")
    with wave.open(path,"wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

def main():
    if not os.path.exists(PRODUCT) or not os.path.exists(LOGO):
        raise FileNotFoundError("Expected both uploaded image files in the repository root.")
    product=Image.open(PRODUCT)
    logo=Image.open(LOGO)
    scenes=[
        scene_open(),
        scene_product(product,1),
        scene_sizes(product),
        scene_price(),
        scene_outro(logo)
    ]
    for i,s in enumerate(scenes,1):
        s.save(f"scene-{i}.png",quality=95)
    duration=SCENE_SECONDS*5-XFADE*4
    make_audio("ambient.wav",duration)
    for i in range(1,6):
        cmd=[
            FFMPEG,"-y","-hide_banner","-loglevel","error",
            "-loop","1","-framerate",str(FPS),"-i",f"scene-{i}.png",
            "-t",str(SCENE_SECONDS),
            "-vf",f"zoompan=z='min(1.055,1+0.00035*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
            "-an","-c:v","libx264","-preset","veryfast","-crf","19",
            f"segment-{i}.mp4"
        ]
        subprocess.run(cmd,check=True)
    inputs=[]
    for i in range(1,6): inputs += ["-i",f"segment-{i}.mp4"]
    fc=(
        f"[0:v][1:v]xfade=transition=fade:duration={XFADE}:offset=3.25[v1];"
        f"[v1][2:v]xfade=transition=fade:duration={XFADE}:offset=6.50[v2];"
        f"[v2][3:v]xfade=transition=fade:duration={XFADE}:offset=9.75[v3];"
        f"[v3][4:v]xfade=transition=fade:duration={XFADE}:offset=13.00,format=yuv420p[v]"
    )
    subprocess.run([
        FFMPEG,"-y","-hide_banner","-loglevel","error",*inputs,
        "-filter_complex",fc,"-map","[v]","-r",str(FPS),
        "-c:v","libx264","-preset","medium","-crf","19",
        "-pix_fmt","yuv420p","-movflags","+faststart","video-silent.mp4"
    ],check=True)
    subprocess.run([
        FFMPEG,"-y","-hide_banner","-loglevel","error",
        "-i","video-silent.mp4","-i","ambient.wav",
        "-map","0:v:0","-map","1:a:0","-c:v","copy",
        "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",OUT
    ],check=True)
    print(f"Created {OUT} ({duration:.2f}s, {W}x{H}, {FPS}fps)")

if __name__=="__main__":
    main()
