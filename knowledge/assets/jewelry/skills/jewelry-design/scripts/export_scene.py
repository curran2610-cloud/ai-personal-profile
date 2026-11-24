"""Blender-side evidence export. Requires saved scene and semantic vertex groups."""
import bpy,sys,json,hashlib,argparse
from pathlib import Path
from mathutils import Vector

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def topology(mesh):return digest({'vertices':len(mesh.vertices),'polygons':[list(p.vertices) for p in mesh.polygons]})
def export(project_id):
    s=bpy.context.scene;frame=bpy.data.objects.get('JEWELRY_FRAME')
    result={'schema':1,'project_id':project_id,'frame_id':'JEWELRY_FRAME','elements':{},'errors':[],'cameras':[],'unit':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length},'baseline_approval':'not_asserted_by_exporter'}
    model=Path(bpy.data.filepath)
    if not bpy.data.filepath or not model.is_file():raise ValueError('Save model before exporting evidence')
    if bpy.data.is_dirty:raise ValueError('Unsaved scene changes; save model before exporting evidence')
    h=hashlib.sha256()
    with model.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    result['model_path']=str(model);result['model_sha256']=h.hexdigest()
    deps=bpy.context.evaluated_depsgraph_get()
    if frame is None:result['errors'].append('Missing JEWELRY_FRAME')
    else:
        frame_world=frame.evaluated_get(deps).matrix_world
        result['frame_matrix_world']=[list(row) for row in frame_world]
        result['frame_world_parity']=1 if frame_world.to_3x3().determinant()>0 else -1
        if abs(frame_world.determinant())<1e-9:result['errors'].append('Singular JEWELRY_FRAME');frame=None
    for ob in s.objects:
        if ob.type=='CAMERA':
            cam=ob.evaluated_get(deps)
            result['cameras'].append({'name':ob.name,'type':cam.data.type,'matrix_world':[list(r) for r in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'lens_mm':cam.data.lens,'clip_start':cam.data.clip_start,'clip_end':cam.data.clip_end,'resolution':[s.render.resolution_x,s.render.resolution_y],'resolution_percentage':s.render.resolution_percentage})
        id=ob.get('jewelry_element_id')
        if not id:continue
        if not isinstance(id,str):result['errors'].append('Element ID must be a string');continue
        if id in result['elements']:result['errors'].append('Duplicate ID: '+id);continue
        row={'status':'unverified','object':ob.name};result['elements'][id]=row
        if ob.type!='MESH' or frame is None:row['reason']='Missing mesh or frame';continue
        evaluated=ob.evaluated_get(deps);me=evaluated.to_mesh()
        try:
            basehash=topology(ob.data);evalhash=topology(me)
            if basehash!=evalhash:raise ValueError('Evaluated topology differs; semantic anchors require review')
            rel=frame_world.inverted()@evaluated.matrix_world
            det=rel.to_3x3().determinant()
            if abs(det)<1e-9:raise ValueError('Singular element transform')
            points={};members={}
            for key in ('origin','forward','up','right'):
                group=ob.vertex_groups.get('anchor_'+key)
                if group is None:raise ValueError('Missing anchor_'+key)
                membership=[];total=0;center=Vector((0,0,0))
                for v in ob.data.vertices:
                    for g in v.groups:
                        if g.group==group.index and g.weight>0:
                            membership.append([v.index,round(g.weight,8)]);center+=(rel@me.vertices[v.index].co)*g.weight;total+=g.weight
                if total<=0:raise ValueError('Empty anchor_'+key)
                points[key]=center/total;members[key]=membership
            vectors={k:points[k]-points['origin'] for k in ('forward','up','right')}
            if any(v.length<1e-8 for v in vectors.values()):raise ValueError('Coincident geometry anchors')
            if abs(vectors['forward'].normalized().cross(vectors['up'].normalized()).dot(vectors['right'].normalized()))<1e-4:raise ValueError('Coplanar anchors')
            row.update(status='measured',evidence='evaluated_mesh_vertex_groups',topology_sha256=basehash,anchors_sha256=digest(members),transform_parity=1 if det>0 else -1,directions={k:list(v) for k,v in vectors.items()},anchor_points={k:list(v) for k,v in points.items()},matrix_relative_to_frame=[list(r) for r in rel])
        except ValueError as e:row['reason']=str(e)
        finally:evaluated.to_mesh_clear()
    if not result['elements']:result['errors'].append('No registered directional elements')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project-id',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    path=Path(args.out)
    if path.exists():raise FileExistsError('Refusing to overwrite snapshot: '+str(path))
    report=export(args.project_id);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False)
    print('SNAPSHOT',path)
