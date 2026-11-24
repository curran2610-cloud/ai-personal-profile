import bpy,bmesh,json,struct
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'dragon-white-model-v002.blend'))
def clean(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    for i in range(6):
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        if not any(f.calc_area()<1e-10 for f in bm.faces):break
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    report={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'volume_mm3':bm.calc_volume(signed=True),'vertices':len(bm.verts),'faces':len(bm.faces)}
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    return report
def export(ob,path):
    me=ob.data;me.calc_loop_triangles()
    with path.open('wb') as f:
        f.write(b'Dragon v002 cleaned prototype / mm'.ljust(80,b' '));f.write(struct.pack('<I',len(me.loop_triangles)))
        for t in me.loop_triangles:
            a,b,c=[ob.matrix_world@me.vertices[i].co for i in t.vertices];n=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
body=bpy.data.objects['DRAGON_BODY_PRINT_MASTER']
report={'pilot_body':clean(body)}
export(body,O/'dragon-v002-pilot-body-mm.stl')
bpy.ops.wm.stl_import(filepath=str(O/'dragon-v002-solid-blank-mm.stl'))
blank=bpy.context.object;report['solid_blank']=clean(blank);export(blank,O/'dragon-v002-solid-blank-mm.stl')
bpy.data.objects.remove(blank,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.wm.save_as_mainfile(filepath=str(O/'dragon-white-model-v002.blend'),compress=True)
(O/'mesh-cleanup-check.json').write_text(json.dumps(report,indent=2))
print('CLEANED',json.dumps(report),flush=True)
