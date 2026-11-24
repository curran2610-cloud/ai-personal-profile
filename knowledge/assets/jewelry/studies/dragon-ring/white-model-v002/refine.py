"""Refine v001 into a single watertight prototype body; millimetre coordinates."""
import bpy,bmesh,math,json,struct,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'white-model-v001/dragon-white-model-v001.blend'))
s=bpy.context.scene
P={'version':'002','inner_diameter_mm':18.2,'voxel_mm':.05,'bevel_mm':.14,'pilot_diameter_factor':.72,'pilot_depth_factor':.40,'minimum_gem_edge_gap_mm':.20,'shrinkage_compensation':1.0,'release':'RESIN PROTOTYPE, NOT CASTING RELEASE'}
(O/'parameters.json').write_text(json.dumps(P,indent=2))
def active(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
def apply(ob,mod):active(ob); bpy.ops.object.modifier_apply(modifier=mod.name)
def recalc(me):
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
def cat(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
# Remove obsolete gem approximations and the independent thin surface overlays.
for ob in list(bpy.data.collections['02_GEM_PLACEHOLDERS'].objects):bpy.data.objects.remove(ob,do_unlink=True)
metal=bpy.data.collections['01_METAL_FORMS']
for ob in list(metal.objects):
    if ob.name.startswith(('Pave_bed','Eye_socket')):bpy.data.objects.remove(ob,do_unlink=True);continue
    if ob.name not in ['Shank_continuous','Head_core_facets']:
        old=[v.co.copy() for v in ob.data.vertices]; stations=[]
        for i in range(0,len(old),4):
            l,ridge,r,bottom=old[i:i+4]
            stations.append(Vector((l.x,(l.y+r.y)/2,l.z,max(abs(r.y-l.y)/2,.35),max(ridge.z-l.z,.30))))
        sampled=[]
        for i in range(len(stations)-1):
            for k in range(10):sampled.append(cat(stations[max(0,i-1)],stations[i],stations[i+1],stations[min(i+2,len(stations)-1)],k/10))
        sampled.append(stations[-1]); vs=[];fs=[]
        for row in sampled:
            x,y,z,w,h=row;w=max(w,.35);h=max(h,.3)
            # Rounded, thicker blade root and a narrow crest instead of razor wedges.
            for yy,zz in [(-w,z),(-.65*w,z+.52*h),(-.12*w,z+h),(.12*w,z+h),(.65*w,z+.52*h),(w,z),(.5*w,z-.85),(-.5*w,z-.85)]:vs.append((x,y+yy,zz))
        for i in range(len(sampled)-1):
            for j in range(8):fs.append((8*i+j,8*(i+1)+j,8*(i+1)+(j+1)%8,8*i+(j+1)%8))
        fs.extend([tuple(range(7,-1,-1)),tuple(8*(len(sampled)-1)+j for j in range(8))])
        me=bpy.data.meshes.new(ob.name+'_refined');me.from_pydata(vs,[],fs);me.update();recalc(me);ob.data=me
    if ob.name!='Shank_continuous':
        be=ob.modifiers.new('Manufacturing edge softening','BEVEL');be.width=P['bevel_mm'];be.segments=3
    for mod in list(ob.modifiers):apply(ob,mod)
# Archive the editable refined sources, hidden from rendering and export.
sources=bpy.data.collections.new('00_EDITABLE_SOURCES_HIDDEN');s.collection.children.link(sources)
for ob in list(metal.objects):
    copy=ob.copy();copy.data=ob.data.copy();sources.objects.link(copy);copy.hide_render=True;copy.hide_set(True)
sources.hide_render=True;sources.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
for ob in metal.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=list(metal.objects)[0];bpy.ops.object.join()
body=bpy.context.object;body.name='DRAGON_BODY_PRINT_MASTER'
# Reinforce the thin lower muzzle junction exposed by the first thickness scan.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(-12.35,0,6.1))
nose=bpy.context.object;nose.name='Muzzle_root_reinforcement';nose.scale=(1.0,1.1,.8)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
active(body);nose.select_set(True);bpy.ops.object.join()
rem=body.modifiers.new('Solid union 0.05mm','REMESH');rem.mode='VOXEL';rem.voxel_size=P['voxel_mm'];rem.use_smooth_shade=True
apply(body,rem)
sm=body.modifiers.new('Subtle edge relaxation','SMOOTH');sm.factor=.32;sm.iterations=4;apply(body,sm)
recalc(body.data)
print('FUSED',len(body.data.polygons),flush=True)
# Recut true cylindrical bore after union; prevents hidden head structure invading finger space.
def cylinder(name,rad,depth,center,normal):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=rad,depth=depth,location=center)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();return ob
def subtract(cutter):
    mod=body.modifiers.new('Cut '+cutter.name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    apply(body,mod);bpy.data.objects.remove(cutter,do_unlink=True)
subtract(cylinder('Calibrated_finger_bore',P['inner_diameter_mm']/2,50,(0,0,0),(0,1,0)))
# Use the actual fused surface to locate every stone; no floating reference stones.
bm=bmesh.new();bm.from_mesh(body.data);surface=BVHTree.FromBMesh(bm);bm.free()
stones=[]
def addstone(name,d,x,y,z,n):
    n=Vector(n).normalized();guess=Vector((x,y,z));hit,normal,face,dist=surface.ray_cast(guess+n*40,-n,80)
    if hit is None:raise RuntimeError('No metal surface for '+name)
    stones.append({'name':name,'diameter_mm':d,'surface':list(hit),'normal':list(n),'center':list(hit+n*.10)})
for sign,side in [(-1,'L'),(1,'R')]:
    addstone('EYE_'+side,1.8,-5.7,sign*5,12.9,(0,sign,0))
    # Eight gently graduated stones along each crown channel, with deliberate gaps.
    ds=[.8,.8,.8,1.,1.,1.,1.,1.2];x=-4.3
    for k,d in enumerate(ds):
        if k:x+=(ds[k-1]+d)/2+.30
        addstone('CROWN_%s_%02d'%(side,k),d,x,sign*2.45,17,(0,0,1))
    # Two rows on the shoulder; extend down the rear to keep actual stone spacing.
    positions=[(.7,12.0,1.6),(2.7,11.8,1.6),(4.6,11.1,1.4),(6.25,10.1,1.4),(7.65,8.9,1.2),(8.75,7.6,1.2),(2.1,9.7,1.2),(3.8,9.25,1.2),(5.4,8.45,1.2),(6.8,7.25,1.2)]
    for k,(x,z,d) in enumerate(positions):addstone('SHOULDER_%s_%02d'%(side,k),d,x,sign*8,z,(0,sign,0))
# Add actual metal lands under the stone locations so pilot edges do not break
# through adjacent tapered blades. These are unset working allowances.
pads=[]
for row in stones:
    d=row['diameter_mm'];n=Vector(row['normal']);p=Vector(row['surface'])
    pad=cylinder('Setting_stock_'+row['name'],d*.5+.45,1.8,p-n*.65,n)
    bevel=pad.modifiers.new('Rounded land','BEVEL');bevel.width=.12;bevel.segments=3;apply(pad,bevel)
    pads.append(pad)
active(body)
for pad in pads:pad.select_set(True)
bpy.ops.object.join()
rem=body.modifiers.new('Union setting stock','REMESH');rem.mode='VOXEL';rem.voxel_size=P['voxel_mm'];rem.use_smooth_shade=True;apply(body,rem)
sm=body.modifiers.new('Setting transitions','SMOOTH');sm.factor=.25;sm.iterations=3;apply(body,sm)
subtract(cylinder('Final_calibrated_bore',P['inner_diameter_mm']/2,50,(0,0,0),(0,1,0)))
bm=bmesh.new();bm.from_mesh(body.data);surface=BVHTree.FromBMesh(bm);bm.free()
for row in stones:
    n=Vector(row['normal']);p=Vector(row['surface']);hit,no,idx,dist=surface.ray_cast(p+n*5,-n,10)
    if hit is None:raise RuntimeError('Missing setting land')
    row['surface']=list(hit);row['center']=list(hit+n*.10)
# Reinforce opposing thin walls before drilling; keep an auditable count.
reinforcement_counts=[]
for repair_pass in range(2):
    bm=bmesh.new();bm.from_mesh(body.data);tree=BVHTree.FromBMesh(bm)
    centers=[];stride=max(1,len(bm.faces)//24000)
    for face in list(bm.faces)[::stride]:
        c=face.calc_center_median();n=face.normal;hit,no,idx,dist=tree.ray_cast(c-n*.015,-n,3)
        if hit is not None and no.dot(n)<-.90 and dist+.015<.60:
            mid=(c+hit)*.5
            if not any((mid-q).length<.5 for q in centers):centers.append(mid)
    bm.free();reinforcement_counts.append(len(centers))
    if not centers:break
    pieces=[]
    for p in centers:
        for q in [p,Vector((p.x,-p.y,p.z))]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.46,location=q);pieces.append(bpy.context.object)
    active(body)
    for ob in pieces:ob.select_set(True)
    bpy.ops.object.join();rem=body.modifiers.new('Local thin-wall reinforcement','REMESH');rem.mode='VOXEL';rem.voxel_size=P['voxel_mm'];rem.use_smooth_shade=True;apply(body,rem)
    sm=body.modifiers.new('Blend local reinforcement','SMOOTH');sm.factor=.22;sm.iterations=2;apply(body,sm)
    subtract(cylinder('Bore_after_reinforcement',P['inner_diameter_mm']/2,50,(0,0,0),(0,1,0)))
print('LOCAL REINFORCEMENT',reinforcement_counts,flush=True)
# Export a clean fused blank before drilling (useful for testing the silhouette).
def export_stl(ob,path):
    me=ob.data;me.calc_loop_triangles()
    with path.open('wb') as f:
        f.write(b'Dragon ring prototype; coordinates in mm'.ljust(80,b' '));f.write(struct.pack('<I',len(me.loop_triangles)))
        for t in me.loop_triangles:
            a,b,c=[ob.matrix_world@me.vertices[j].co for j in t.vertices];n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
export_stl(body,O/'dragon-v002-solid-blank-mm.stl')
# Pilot recesses preserve metal for a setter, rather than pretending finished seats.
cutters=[]
for row in stones:
    d=row['diameter_mm'];n=Vector(row['normal']);p=Vector(row['surface']);depth=d*P['pilot_depth_factor']
    cutter=cylinder('Pilot_'+row['name'],d*.5*P['pilot_diameter_factor'],depth+.6,p+n*(.6-depth)/2,n);cutters.append(cutter)
    row['pilot_diameter_mm']=d*P['pilot_diameter_factor'];row['pilot_depth_mm']=depth
# Join the disjoint cutting solids into one boolean tool for efficiency.
bpy.ops.object.select_all(action='DESELECT')
for ob in cutters:ob.select_set(True)
bpy.context.view_layer.objects.active=cutters[0];bpy.ops.object.join();subtract(bpy.context.object)
recalc(body.data)
print('PILOTS CUT',len(body.data.polygons),flush=True)
clay=bpy.data.materials.get('White clay');body.data.materials.clear();body.data.materials.append(clay)
for p in body.data.polygons:p.use_smooth=True
# Independent white gem visualization; not included in STL.
gems=bpy.data.collections['02_GEM_PLACEHOLDERS'];gems.name='02_GEMS_PREVIEW_ONLY'
for row in stones:
    d=row['diameter_mm'];q=Vector((0,0,1)).rotation_difference(Vector(row['normal']));c=Vector(row['center']);vs=[]
    for radius,z in [(d*.29,d*.20),(d*.5,0),(d*.35,-d*.18)]:
        for k in range(16):
            a=2*math.pi*k/16;vs.append(tuple(c+q@Vector((radius*math.cos(a),radius*math.sin(a),z))))
    vs.append(tuple(c+q@Vector((0,0,-d*.44))))
    fs=[tuple(range(16))]
    for i in range(2):
        for k in range(16):fs.append((16*i+k,16*i+(k+1)%16,16*(i+1)+(k+1)%16,16*(i+1)+k))
    for k in range(16):fs.append((32+k,32+(k+1)%16,48))
    me=bpy.data.meshes.new(row['name']);me.from_pydata(vs,[],fs);me.update();recalc(me)
    ob=bpy.data.objects.new(row['name'],me);gems.objects.link(ob);me.materials.append(bpy.data.materials['Gem placeholders - white']);ob['diameter_mm']=d
# Mesh topology and actual component checks.
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
unseen=set(bm.verts);components=[]
while unseen:
    v=unseen.pop();stack=[v];count=1
    while stack:
        u=stack.pop()
        for e in u.link_edges:
            w=e.other_vert(u)
            if w in unseen:unseen.remove(w);stack.append(w);count+=1
    components.append(count)
report={'version':'002','unit':'mm','vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'components_vertex_counts':sorted(components,reverse=True),'signed_volume_mm3':bm.calc_volume(signed=True),'bounds_mm':{a:max(v.co[k] for v in bm.verts)-min(v.co[k] for v in bm.verts) for k,a in enumerate('XYZ')},'gem_count':len(stones),'voxel_size_mm':P['voxel_mm'],'voxel_note':'Numerical modeling resolution, NOT machine tolerance','release':P['release']}
# Thickness check: ray from each stone pilot floor into the remaining metal.
tree=BVHTree.FromBMesh(bm)
for row in stones:
    n=Vector(row['normal']);origin=Vector(row['surface'])-n*(row['pilot_depth_mm']+.015)
    hit,no,idx,dist=tree.ray_cast(origin,-n,40)
    row['floor_remaining_ray_mm']=None if hit is None else dist
# Sample local normal thickness; excludes grazing/bad hits, not a global guarantee.
samples=[];parallel_samples=[]
stride=max(1,len(bm.faces)//12000)
for face in list(bm.faces)[::stride]:
    c=face.calc_center_median();n=face.normal
    hit,no,idx,dist=tree.ray_cast(c-n*.015,-n,40)
    if hit is not None and no.dot(n)<-.15:
        samples.append((dist+.015,list(c)))
        if no.dot(n)<-.9:parallel_samples.append((dist+.015,list(c)))
samples.sort()
report['thickness_samples_count']=len(samples)
report['thickness_min_sample_mm']=samples[0][0] if samples else None
report['thickness_samples_below_0_5_mm']=sum(x[0]<.5 for x in samples)
report['thinnest_sample_locations']=samples[:15]
parallel_samples.sort()
report['near_parallel_wall_min_sample_mm']=parallel_samples[0][0] if parallel_samples else None
report['near_parallel_wall_samples_below_0_5_mm']=sum(x[0]<.5 for x in parallel_samples)
report['thickness_method_limit']='Normal ray sampling is not a certified global wall-thickness test. Edge/grazing hits remain flagged.'
report['local_reinforcement_counts']=reinforcement_counts
report['minimum_pilot_floor_ray_mm']=min((row['floor_remaining_ray_mm'] for row in stones if row['floor_remaining_ray_mm'] is not None),default=None)
gaps=[]
for i,a in enumerate(stones):
    for b in stones[i+1:]:
        gap=(Vector(a['center'])-Vector(b['center'])).length-(a['diameter_mm']+b['diameter_mm'])/2
        gaps.append((gap,a['name'],b['name']))
report['min_gem_bounding_sphere_gap_mm']=min(gaps)
bm.free()
(O/'stone-layout.json').write_text(json.dumps(stones,indent=2))
(O/'validation.json').write_text(json.dumps(report,indent=2))
export_stl(body,O/'dragon-v002-pilot-body-mm.stl')
active(body);s.camera=bpy.data.objects['CAM_HERO']
s.render.resolution_x=1600;s.render.resolution_y=1600
s.display.shading.curvature_ridge_factor=1.1;s.display.shading.curvature_valley_factor=1.0
body['release']=P['release'];body['voxel_mm']=P['voxel_mm'];body['pilot_recesses']=38
tx=bpy.data.texts.new('V002_PARAMETERS_AND_RELEASE');tx.write(json.dumps(P,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'dragon-white-model-v002.blend'))
for name in ['hero','top','side','front']:
    s.camera=bpy.data.objects['CAM_'+name.upper()];s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
gems.hide_render=True;s.camera=bpy.data.objects['CAM_HERO'];s.render.filepath=str(O/'body-only.png');bpy.ops.render.render(write_still=True)
print('VALIDATION',json.dumps(report),flush=True)
