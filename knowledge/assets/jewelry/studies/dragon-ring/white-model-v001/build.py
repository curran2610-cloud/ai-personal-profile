import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
P={'inner_diameter_mm':18.2,'bottom_width_mm':6.5,'bottom_thickness_mm':2.0,'head_width_mm':17.0,'head_height_reference_mm':10.0,'size_assumption':'#8 interpreted provisionally as US 8','gem_diameters_counts':{'0.8':6,'1.0':8,'1.2':14,'1.4':4,'1.6':4,'1.8':2}}
pf=O/'parameters.json'
if pf.exists(): P=json.loads(pf.read_text())
else: pf.write_text(json.dumps(P,indent=2))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=.001; s.unit_settings.length_unit='MILLIMETERS'
def material(name,value):
    m=bpy.data.materials.new(name); m.diffuse_color=(value,value,value,1); return m
clay=material('White clay',.78); inset=material('Recess clay',.48); stone=material('Gem placeholders - white',.95)
metal=bpy.data.collections.new('01_METAL_FORMS'); s.collection.children.link(metal)
gems=bpy.data.collections.new('02_GEM_PLACEHOLDERS'); s.collection.children.link(gems)
def meshobj(name,vs,fs,mat=clay,collection=metal,smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); me.materials.append(mat)
    for f in me.polygons:f.use_smooth=smooth
    return ob
# Ring axis Y; head points toward negative X. A continuous comfort-bore shank.
r=P['inner_diameter_mm']/2; n=192; vs=[]; fs=[]
for i in range(n):
    t=2*math.pi*i/n; top=(math.sin(t)+1)/2
    w=P['bottom_width_mm']+(P['head_width_mm']-P['bottom_width_mm'])*top**3
    thick=P['bottom_thickness_mm']+.45*top**3
    for radius,y in [(r,-w/2),(r,w/2),(r+thick,w/2),(r+thick,-w/2)]:vs.append((radius*math.cos(t),y,radius*math.sin(t)))
for i in range(n):
    for j in range(4):fs.append((4*i+j,4*((i+1)%n)+j,4*((i+1)%n)+(j+1)%4,4*i+(j+1)%4))
band=meshobj('Shank_continuous',vs,fs,smooth=True)
bev=band.modifiers.new('Soft inner and outer edges','BEVEL'); bev.width=.22; bev.segments=3
# Faceted closed head shell, blending narrow muzzle into broad crown.
sections=[(-13.0,.38,5.6,6.5),(-11.8,1.7,7.0,9.0),(-9.6,2.8,9.3,11.3),(-6.8,4.0,10.5,13.3),(-3.2,5.5,11.0,15.0),(1.0,6.6,10.8,15.5),(5.4,7.2,9.4,14.6),(9.0,5.7,6.9,11.6),(10.6,3.8,4.0,8.5)]
vs=[]
for x,w,lo,hi in sections:
    vs.extend([(x,-w,lo),(x,-w,hi-.9),(x,-w*.44,hi+.15),(x,0,hi+.65),(x,w*.44,hi+.15),(x,w,hi-.9),(x,w,lo),(x,0,lo-.4)])
fs=[]
for i in range(len(sections)-1):
    for j in range(8):fs.append((8*i+j,8*(i+1)+j,8*(i+1)+(j+1)%8,8*i+(j+1)%8))
fs.extend([tuple(range(7,-1,-1)),tuple(8*(len(sections)-1)+j for j in range(8))])
meshobj('Head_core_facets',vs,fs)
# Each ridge is a closed faceted blade, with a peaked central spine.
def blade(name,stations,mat=clay):
    vs=[]
    for x,y,z,w,h in stations:vs.extend([(x,y-w,z),(x,y,z+h),(x,y+w,z),(x,y,z-.32)])
    fs=[]
    for i in range(len(stations)-1):
        for j in range(4):fs.append((4*i+j,4*(i+1)+j,4*(i+1)+(j+1)%4,4*i+(j+1)%4))
    fs.extend([(3,2,1,0),tuple(4*(len(stations)-1)+j for j in range(4))])
    return meshobj(name,vs,fs,mat)
blade('Central_nose_to_crest',[(-13.1,0,6.4,.12,.25),(-11.6,0,9.15,.85,.7),(-8.0,0,12.4,1.0,.95),(-3,0,15.4,1.1,1.15),(2.5,0,16.4,.8,1.2),(6.6,0,18.3,.04,.12)])
for sign,side in [(-1,'L'),(1,'R')]:
    def st(rows):return [(x,sign*y,z,w,h) for x,y,z,w,h in rows]
    blade('Brow_long_'+side,st([(-11.3,1.2,9,.15,.25),(-8,2.3,11.6,.75,.7),(-4.4,3.4,14.0,1.05,.85),(0,4.1,16.0,.95,1),(4.3,4.5,18,.04,.12)]))
    blade('Eye_upper_ridge_'+side,st([(-7.7,3.6,12.1,.1,.15),(-5.5,4.7,14.1,.7,.65),(-1.3,5.7,15.8,.9,.75),(4.9,6.0,17.5,.04,.12)]))
    blade('Jaw_sweep_'+side,st([(-12.7,.9,6.3,.12,.2),(-10.5,2.4,8.3,.5,.5),(-7.2,4.3,10.7,.65,.5),(-3.7,5.8,12.3,.9,.65),(2.0,7.5,14.1,.04,.12)]))
    blade('Eye_socket_'+side,st([(-7.0,4.2,12.0,.08,.03),(-5.3,5.1,12.8,.85,.12),(-2.9,5.8,13.4,.08,.02)]),inset)
    # Swept overlapping armor plates, increasing toward the back.
    for k in range(4):
        x=-2.3+k*2.9; z=13.7-k*.65; y=5.8+k*.15
        blade('Swept_armor_%s_%02d'%(side,k),st([(x-2.2,y-.35,z-.8,.14,.2),(x,y,z,.85,.75),(x+2.1,y+.15,z+.5,1.0,.6),(x+3.9,min(y+.5,8.2),z+1.4,.05,.12)]))
    for k in range(3):
        x=3.0+k*2.1; z=15.0-k*1.2
        blade('Crown_scale_%s_%02d'%(side,k),st([(x-2,1.8,z,.08,.2),(x,2.5,z+.5,1.3,.7),(x+3.0,3.1,z+.9,.04,.1)]))
    # Pavé bed on the broad rear shoulder, intentionally separate for later editing.
    meshobj('Pave_bed_'+side,[(0,sign*6.7,12.1),(4.8,sign*7.65,11.5),(9.0,sign*6.0,5.8),(5.8,sign*7.0,7.2),(0,sign*6.55,11.85),(4.8,sign*7.5,11.25),(9,sign*5.85,5.55),(5.8,sign*6.85,6.95)],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],inset)
def gem(name,center,d,normal):
    normal=Vector(normal).normalized(); q=Vector((0,0,1)).rotation_difference(normal)
    vs=[]
    for rad,z in [(d*.29,d*.20),(d*.5,0),(d*.34,-d*.20)]:
        for k in range(8):
            a=2*math.pi*k/8; v=q@Vector((rad*math.cos(a),rad*math.sin(a),z))+Vector(center); vs.append(tuple(v))
    vs.append(tuple(q@Vector((0,0,-d*.45))+Vector(center)))
    fs=[tuple(range(8))]
    for level in range(2):
        for k in range(8):fs.append((level*8+k,level*8+(k+1)%8,(level+1)*8+(k+1)%8,(level+1)*8+k))
    for k in range(8):fs.append((16+k,16+(k+1)%8,24))
    ob=meshobj(name,vs,fs,stone,gems); ob['diameter_mm']=d
for sign,side in [(-1,'L'),(1,'R')]:
    gem('Eye_'+side,(-5.2,sign*5.15,13.05),1.8,(0,sign*.75,.65))
    # 8 forehead stones per side.
    for k,d in enumerate([.8,.8,.8,1,1,1,1,1.2]):
        x=-3.2+k*.95; gem('Forehead_%s_%02d'%(side,k),(x,sign*(3.9+k*.05),15.2+k*.16),d,(0,sign*.25,1))
    # 10 rear shoulder stones per side; counts match annotated RD list.
    coords=[(1.0,12.0),(2.5,11.8),(4,11.3),(5.4,10.6),(6.6,9.7),(7.5,8.6),(3.0,10.2),(4.5,9.5),(5.6,8.6),(6.4,7.5)]
    for k,((x,z),d) in enumerate(zip(coords,[1.6,1.6,1.4,1.4,1.2,1.2,1.2,1.2,1.2,1.2])):
        y=7.65-.065*(x-3)**2
        gem('Shoulder_%s_%02d'%(side,k),(x,sign*y,z),d,(0,sign, .25))
# Scene setup. Material-neutral clay, all views use identical geometry and scale.
s.render.engine='BLENDER_WORKBENCH'; sh=s.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'
sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=1.3; sh.curvature_valley_factor=1.1
sh.show_specular_highlight=True; sh.background_type='WORLD'; s.world.color=(1,1,1)
s.render.film_transparent=True; s.render.resolution_x=1100; s.render.resolution_y=1100; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='Standard'
target=Vector((0,0,3.5)); cams={}
for name,offset in [('hero',(-42,-60,38)),('top',(0,0,70)),('side',(0,-70,0)),('front',(-70,0,0))]:
    ca=bpy.data.cameras.new('CAM_'+name.upper()); ca.type='ORTHO'; ca.ortho_scale=37; ca.clip_end=300; ca.clip_start=.1
    ob=bpy.data.objects.new(ca.name,ca); s.collection.objects.link(ob); ob.location=target+Vector(offset); ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler(); cams[name]=ob
s.camera=cams['hero']
for ob in bpy.context.selected_objects: ob.select_set(False)
band.select_set(True); bpy.context.view_layer.objects.active=band
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_location=target; a.spaces.active.region_3d.view_distance=48
            a.spaces.active.region_3d.view_rotation=cams['hero'].rotation_euler.to_quaternion()
checks={}; points=[]
for ob in list(metal.objects)+list(gems.objects):
    bm=bmesh.new(); bm.from_mesh(ob.data); checks[ob.name]={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)}; bm.free()
    points.extend([ob.matrix_world@v.co for v in ob.data.vertices])
counts={}
for ob in gems.objects:
    key=str(ob['diameter_mm']); counts[key]=counts.get(key,0)+1
report={'bounds_mm':{a:max(v[k] for v in points)-min(v[k] for v in points) for k,a in enumerate('XYZ')},'metal_parts':len(metal.objects),'gem_count':len(gems.objects),'gem_counts':counts,'raw_mesh_checks':checks,'status':'Separate intersecting modeling components, NOT fused manufacturing mesh','unverified':['gem seating and clearances','reference 37g mass','interpretation of 10mm dimension','wear comfort','minimum wall thickness','intersections between parts']}
(O/'measurements.json').write_text(json.dumps(report,indent=2))
tx=bpy.data.texts.new('PARAMETERS'); tx.write(json.dumps(P,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'dragon-white-model-v001.blend'))
for name,ca in cams.items():
    s.camera=ca; s.render.filepath=str(O/(name+'.png')); bpy.ops.render.render(write_still=True)
print('DONE',json.dumps({k:v for k,v in report.items() if k!='raw_mesh_checks'}))
