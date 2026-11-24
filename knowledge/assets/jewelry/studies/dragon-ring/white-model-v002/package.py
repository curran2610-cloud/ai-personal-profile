from pathlib import Path
import json,struct,numpy as np
from PIL import Image,ImageDraw,ImageFont
o=Path(__file__).resolve().parent
dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
out={}
for name in ['dragon-v002-solid-blank-mm.stl','dragon-v002-pilot-body-mm.stl']:
    p=o/name
    with p.open('rb') as f:
        f.seek(80);count=struct.unpack('<I',f.read(4))[0]
    data=np.memmap(p,dtype=dtype,mode='r',offset=84,shape=(count,))
    vs=data['v'];bounds=vs.max(axis=(0,1))-vs.min(axis=(0,1));volume=0.;degenerate=0
    for start in range(0,count,100000):
        v=np.asarray(vs[start:start+100000],dtype=np.float64)
        cross=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);degenerate+=int(np.count_nonzero(np.linalg.norm(cross,axis=1)<1e-10))
        volume+=float(np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])).sum()/6)
    out[name]={'triangle_count':count,'byte_length_valid':p.stat().st_size==84+count*50,'finite_vertices':bool(np.isfinite(vs).all()),'bounds_mm':bounds.tolist(),'signed_volume_mm3':volume,'degenerate_triangles':degenerate}
(o/'stl-roundtrip-check.json').write_text(json.dumps(out,indent=2))
im=Image.new('RGB',(2100,2080),'#f6f6f3');d=ImageDraw.Draw(im)
font='/System/Library/Fonts/Helvetica.ttc';title=ImageFont.truetype(font,44);label=ImageFont.truetype(font,28);small=ImageFont.truetype(font,24)
d.text((70,42),'DRAGON RING / SOLID CLAY V002',font=title,fill='#222222')
d.text((70,105),'Continuous body | Rounded blade transitions | 38 pilot locations | mm',font=small,fill='#666666')
for name,x,y,caption in [('body-only',30,150,'SOLID BODY / pilot recesses'),('top',1070,150,'TOP / gem preview'),('front',30,1060,'FRONT / gem preview'),('side',1070,1060,'SIDE / gem preview')]:
    pic=Image.open(o/(name+'.png')).convert('RGBA').resize((970,970));im.paste(pic,(x,y),pic);d.text((x+35,y+900),caption,font=label,fill='#333333')
d.text((70,2015),'Resin prototype study. Pilot recesses are not finished gem settings. No casting shrinkage applied.',font=small,fill='#555555')
im.save(o/'review-sheet.png')
print(json.dumps(out,indent=2))
