from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
o=Path(__file__).resolve().parent
im=Image.new('RGB',(1800,1860),'#f6f6f3'); d=ImageDraw.Draw(im)
font='/System/Library/Fonts/Helvetica.ttc'
title=ImageFont.truetype(font,38); label=ImageFont.truetype(font,26); small=ImageFont.truetype(font,23)
d.text((65,40),'DRAGON RING / CLAY BLOCKOUT 001',font=title,fill='#252525')
d.text((65,103),'Blender geometry study | Same model in all views | Provisional reconstruction',font=small,fill='#666666')
for name,x,y,caption in [('hero',40,160,'OBLIQUE / form review'),('top',920,160,'TOP / +Z'),('front',40,950,'HEAD-ON / -X'),('side',920,950,'SIDE / -Y')]:
    pic=Image.open(o/(name+'.png')).convert('RGBA').resize((810,810))
    im.paste(pic,(x,y),pic)
    d.text((x+35,y+760),caption,font=label,fill='#333333')
d.text((65,1790),'ID 18.2 mm (assumed) | Width 17 mm | Base shank 6.5 x 2 mm | 38 stone placeholders',font=small,fill='#444444')
im.save(o/'review-sheet.png')
