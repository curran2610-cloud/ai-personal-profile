"""Integration test in temporary directory; no project design is created."""
import bpy,importlib.util,json,tempfile,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ex=module('export_scene');w=module('workflow')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
frame=bpy.data.objects.new('JEWELRY_FRAME',None);bpy.context.scene.collection.objects.link(frame)
me=bpy.data.meshes.new('Fixture');me.from_pydata([(0,0,0),(2,0,0),(0,0,2),(0,-2,0)],[],[(0,1,2),(0,3,1),(0,2,3),(1,3,2)])
ob=bpy.data.objects.new('Directional_fixture',me);bpy.context.scene.collection.objects.link(ob);ob.parent=frame;ob['jewelry_element_id']='fixture'
for i,key in enumerate(['origin','forward','up','right']):ob.vertex_groups.new(name='anchor_'+key).add([i],1,'REPLACE')
cam=bpy.data.objects.new('Check_camera',bpy.data.cameras.new('Check_camera'));bpy.context.scene.collection.objects.link(cam);cam.data.type='ORTHO'
checks={}
with tempfile.TemporaryDirectory(prefix='jewelry-evidence-') as t:
    def snap():
        bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(Path(t)/'fixture.blend'));return ex.export('integration-test')
    baseline=snap();assert baseline['elements']['fixture']['status']=='measured',baseline
    frame.rotation_euler.z=math.pi
    checks['whole_model_rotation']=w.compare(baseline,snap())['status'];assert checks['whole_model_rotation']=='pass'
    cam.location=(9,8,7)
    checks['camera_change']=w.compare(baseline,snap())['status'];assert checks['camera_change']=='pass'
    frame.scale.x=-1
    checks['whole_model_mirror']=w.compare(baseline,snap())['status'];assert checks['whole_model_mirror']=='fail'
    frame.scale.x=1
    ob.rotation_euler.x=math.pi
    checks['element_flip']=w.compare(baseline,snap())['status'];assert checks['element_flip']=='fail'
    ob.rotation_euler.x=0
    for v in me.vertices:v.co.x*=-1
    checks['baked_mesh_flip']=w.compare(baseline,snap())['status'];assert checks['baked_mesh_flip']=='fail'
    for v in me.vertices:v.co.x*=-1
    ob.modifiers.new('Topology change','SUBSURF').levels=1
    checks['evaluated_topology_change']=w.compare(baseline,snap())['status'];assert checks['evaluated_topology_change']=='unverified'
print('INTEGRATION_PASS',json.dumps(checks))
