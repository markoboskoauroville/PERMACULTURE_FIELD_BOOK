#!/usr/bin/env python3
"""raw/*.jpg -> images/*.jpg, dissolving bare paper into #16110D.
Paper = bright, low-saturation AND connected to the image border. The border
condition is what stops a warmly lit interior wall being mistaken for paper."""
import os, numpy as np
from PIL import Image, ImageFilter, ImageDraw
BG=(0x16,0x11,0x0D); RAW='raw'; OUT='images'

def paper_mask(a):
    lum=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]; sat=a.max(-1)-a.min(-1)
    cand=((lum>200)&(sat<55)).astype(np.uint8)*255
    h,w=cand.shape
    padded=Image.new('L',(w+2,h+2),255)          # 1px paper frame to seed from
    padded.paste(Image.fromarray(cand),(1,1))
    ImageDraw.floodfill(padded,(0,0),128)        # flood only border-connected paper
    flooded=np.asarray(padded)[1:h+1,1:w+1]
    return Image.fromarray(((flooded==128)*255).astype(np.uint8))

def seat(name):
    im=Image.open(f'{RAW}/{name}').convert('RGB')
    p=paper_mask(np.asarray(im).astype(np.float32))
    p=p.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))  # close flecks
    p=p.filter(ImageFilter.MinFilter(3))                                   # never bite the paint
    keep=Image.fromarray(255-np.asarray(p)).filter(ImageFilter.GaussianBlur(2.4))
    out=Image.new('RGB',im.size,BG); out.paste(im,(0,0),keep)
    out.save(f'{OUT}/{name}',quality=88,optimize=True)
    return round(100*(np.asarray(p)>127).mean(),1)

for n in sorted(os.listdir(RAW)):
    print(f"  {n}: {seat(n)}% paper dissolved")
