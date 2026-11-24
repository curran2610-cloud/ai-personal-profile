from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent
sheet=Image.new('RGB',(1800,1740),'#f7f7f4')
d=ImageDraw.Draw(sheet)
font='/System/Library/Fonts/Helvetica.ttc'
title=ImageFont.truetype(font,36)
label=ImageFont.truetype(font,25)
small=ImageFont.truetype(font,21)
d.text((70,40),'BOIS DE ROSE / WHITE MODEL 001',font=title,fill='#252525')
d.text((70,98),'Single mesh / Orthographic views / millimetres / provisional geometry',font=small,fill='#666666')
for name,x,y,caption in [('top',70,155,'TOP / camera +Z'),('hero',950,155,'OBLIQUE / shape review'),('front',70,885,'FRONT / camera -Y'),('right',950,885,'RIGHT / camera +X')]:
    im=Image.open(root/(name+'.png')).convert('RGBA').resize((720,720))
    sheet.paste(im,(x,y),im)
    d.text((x,y+680),caption,font=label,fill='#333333')
d.text((70,1680),'ID 16.5 | Radial thickness 1.6 | Base width 2.0 | Overall axial height 4.96 mm',font=small,fill='#333333')
sheet.save(root/'review-sheet.png')
