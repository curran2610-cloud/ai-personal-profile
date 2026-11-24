import bpy,bmesh,json,struct
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(O/'dragon-v002-solid-blank-mm.stl'))
ob=bpy.context.object
mod=ob.modifiers.new('Clean blank volume','REMESH');mod.mode='VOXEL';mod.voxel_size=.05;mod.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(ob.data)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
report={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'volume_mm3':bm.calc_volume(signed=True),'cleanup_voxel_mm':.05,'note':'Backup blank remeshed independently; final dimensions differ slightly from pilot body.'}
bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
with (O/'dragon-v002-solid-blank-mm.stl').open('wb') as f:
    f.write(b'Dragon v002 cleaned blank / mm'.ljust(80,b' '));f.write(struct.pack('<I',len(ob.data.loop_triangles)))
    for t in ob.data.loop_triangles:
        a,b,c=[ob.matrix_world@ob.data.vertices[i].co for i in t.vertices];n=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
(O/'blank-cleanup-check.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
