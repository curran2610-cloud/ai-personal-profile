"""Run with Blender --background --python build.py. One model, four cameras."""
import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
P = {
    'version': 'white-model-v001', 'units': 'mm',
    'inner_diameter_mm': 16.5, 'radial_thickness_mm': 1.6,
    'base_axial_width_mm': 2.0, 'wave_amplitude_mm': 0.45,
    'thorn_nodes': [
        {'angle_deg': 25, 'height_mm': 1.9, 'width_deg': 10, 'side': 1},
        {'angle_deg': 142, 'height_mm': 1.65, 'width_deg': 12, 'side': 1},
        {'angle_deg': 257, 'height_mm': 1.45, 'width_deg': 10, 'side': 1},
        {'angle_deg': 205, 'height_mm': 0.7, 'width_deg': 13, 'side': -1},
        {'angle_deg': 330, 'height_mm': 0.85, 'width_deg': 13, 'side': -1}],
    'orthographic_scale_mm': 25.0,
    'status': 'Approximate study; dimensions and hidden geometry are assumptions.'
}
params = OUT / 'parameters.json'
if params.exists():
    P = json.loads(params.read_text())
else:
    params.write_text(json.dumps(P, ensure_ascii=False, indent=2))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
scene.unit_settings.length_unit = 'MILLIMETERS'
N, M = 640, 64
verts, faces = [], []
inner = P['inner_diameter_mm']/2
thick = P['radial_thickness_mm']
for i in range(N):
    t = 2*math.pi*i/N
    zc = P['wave_amplitude_mm']*(math.sin(3*t+.4)+.3*math.sin(2*t-.6))
    up = down = 0.0
    for node in P['thorn_nodes']:
        delta = math.atan2(math.sin(t-math.radians(node['angle_deg'])), math.cos(t-math.radians(node['angle_deg'])))
        bump = node['height_mm']*math.exp(-.5*(delta/math.radians(node['width_deg']))**2)
        if node['side']>0: up += bump
        else: down += bump
    for j in range(M):
        a = 2*math.pi*j/M
        # Circular inner envelope stays fixed; thorns rise axially on outer half.
        r = inner + thick*.5*(1+math.cos(a))
        s = math.sin(a)
        outer_weight = ((1+math.cos(a))*.5)**.6
        z = zc + P['base_axial_width_mm']*.5*s
        z += (up if s>=0 else -down)*abs(s)**1.6*outer_weight
        verts.append((r*math.cos(t), r*math.sin(t), z))
for i in range(N):
    for j in range(M):
        a=i*M+j; b=((i+1)%N)*M+j
        faces.append((a,b,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M))
mesh=bpy.data.meshes.new('Continuous_Stem_Mesh')
mesh.from_pydata(verts,[],faces); mesh.update()
bm=bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(mesh); bm.free()
ring=bpy.data.objects.new('RING_001_Continuous_Stem',mesh)
scene.collection.objects.link(ring)
for f in mesh.polygons: f.use_smooth=True
ring.color=(.78,.78,.78,1)
for key in ['inner_diameter_mm','radial_thickness_mm','base_axial_width_mm','wave_amplitude_mm']:
    ring[key]=P[key]
ring['source']='Dior Bois de Rose photo study; approximate, not measured replica'
mat=bpy.data.materials.new('Neutral_White_Clay'); mat.diffuse_color=(.78,.78,.78,1)
mesh.materials.append(mat)
scene.render.engine='BLENDER_WORKBENCH'
sh=scene.display.shading
sh.light='STUDIO'; sh.studiolight_rotate_z=.5
sh.color_type='MATERIAL'; sh.show_shadows=True
sh.show_cavity=True; sh.cavity_type='BOTH'
sh.curvature_ridge_factor=1.2; sh.curvature_valley_factor=1.0
sh.show_specular_highlight=True
sh.background_type='WORLD'; scene.world.color=(1,1,1)
scene.render.film_transparent=True
scene.render.resolution_x=1000; scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
cameras={}
for name, loc in [('top',(0,0,60)),('front',(0,-60,0)),('right',(60,0,0)),('hero',(30,-45,29))]:
    data=bpy.data.cameras.new('CAM_'+name.upper()); data.type='ORTHO'
    data.ortho_scale=P['orthographic_scale_mm']; data.clip_start=.1; data.clip_end=300
    obj=bpy.data.objects.new(data.name,data); scene.collection.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
    cameras[name]=obj
scene.camera=cameras['hero']
bpy.context.view_layer.objects.active=ring; ring.select_set(True)
for obj in bpy.context.selected_objects:
    if obj!=ring: obj.select_set(False)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=33
            area.spaces.active.region_3d.view_rotation=cameras['hero'].rotation_euler.to_quaternion()
bm=bmesh.new(); bm.from_mesh(mesh)
stats={'vertices':len(mesh.vertices),'faces':len(mesh.polygons),
       'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
       'volume_mm3':abs(bm.calc_volume(signed=True)),
       'actual_inner_diameter_mm':2*min(math.hypot(v.co.x,v.co.y) for v in mesh.vertices),
       'bounds_mm':{axis:max(v.co[k] for v in mesh.vertices)-min(v.co[k] for v in mesh.vertices) for k,axis in enumerate('XYZ')},
       'camera_scale_mm':{name:cam.data.ortho_scale for name,cam in cameras.items()},
       'not_checked':['self intersections','minimum wall thickness','comfort','manufacturing suitability']}
bm.free()
(OUT/'measurements.json').write_text(json.dumps(stats,indent=2))
text=bpy.data.texts.new('PARAMETERS_AND_ASSUMPTIONS'); text.write(json.dumps(P,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'white-model-v001.blend'))
for name, cam in cameras.items():
    scene.camera=cam; scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
print('MODEL_CHECK',json.dumps(stats))
