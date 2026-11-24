"""Project inventory, non-overwriting versions, and semantic orientation checks."""
import argparse, hashlib, json, math, re
from pathlib import Path
from datetime import datetime, timezone

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)

def inventory(project):
    root=Path(project).resolve();entries=[]
    if not root.is_dir():raise ValueError('Project directory not found')
    for p in sorted(root.rglob('*')):
        if any(part in {'.git','__pycache__','.DS_Store'} for part in p.relative_to(root).parts):continue
        if p.is_symlink():
            entries.append({'path':str(p.relative_to(root)),'read_status':'symlink_not_followed'});continue
        if p.is_file():entries.append({'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size,'read_status':'not_read','role':'unclassified'})
    return {'project_root':str(root),'files':entries,'note':'Inventory is not evidence of reading or understanding.'}

def new_version(project,reason):
    root=Path(project).resolve()
    if not root.is_dir():raise ValueError('Project directory not found')
    versions=root/'versions';versions.mkdir(exist_ok=True)
    while True:
        existing=sorted(int(p.name[1:]) for p in versions.iterdir() if p.is_dir() and re.fullmatch(r'v\d{3,}',p.name))
        n=max(existing,default=0)+1;out=versions/f'v{n:03d}'
        try:out.mkdir()
        except FileExistsError:continue
        break
    write_new(out/'manifest.json',{'version':out.name,'parent_version':f'v{max(existing):03d}' if existing else None,'created_utc':datetime.now(timezone.utc).isoformat(),'reason':reason,'status':'draft','approval':None,'artifacts':[]})
    return out

def vec(value):
    if not isinstance(value,list) or len(value)!=3:raise ValueError('Expected 3-vector')
    v=[float(x) for x in value]
    if not all(math.isfinite(x) for x in v):raise ValueError('Non-finite vector')
    length=math.sqrt(sum(x*x for x in v))
    if length<1e-8:raise ValueError('Degenerate vector')
    return [x/length for x in v]

def triple(d):
    f,u,r=(vec(d[k]) for k in ('forward','up','right'))
    value=(f[1]*u[2]-f[2]*u[1])*r[0]+(f[2]*u[0]-f[0]*u[2])*r[1]+(f[0]*u[1]-f[1]*u[0])*r[2]
    if abs(value)<1e-4:raise ValueError('Coplanar semantic anchors')
    return 1 if value>0 else -1

def compare(base,current,tolerance=1.):
    if not math.isfinite(tolerance) or not 0<=tolerance<90:raise ValueError('Tolerance must be in [0, 90) degrees')
    result={'status':'pass','scope':'relative consistency of registered directions only; not approval of the baseline or manufacturing','baseline_approval_checked':False,'warnings':['Baseline approval must be checked against the version manifest; self-comparison cannot approve an initial orientation.'],'tolerance_deg':tolerance,'checks':[]}
    def add(id,status,detail):result['checks'].append({'element_id':id,'status':status,'detail':detail})
    if base.get('schema')!=1 or current.get('schema')!=1:raise ValueError('Unsupported snapshot schema')
    if not base.get('project_id') or base.get('project_id')!=current.get('project_id'):add('*','fail','Project identity mismatch')
    if not base.get('frame_id') or base.get('frame_id')!=current.get('frame_id'):add('*','fail','Reference-frame identity mismatch')
    if base.get('frame_world_parity') not in (-1,1) or current.get('frame_world_parity') not in (-1,1):add('*','unverified','Missing frame-world handedness evidence')
    elif base['frame_world_parity']!=current['frame_world_parity']:add('*','fail','Whole-model reference frame mirrored')
    if base.get('errors') or current.get('errors'):add('*','unverified','Snapshot extraction errors')
    a=base.get('elements',{});b=current.get('elements',{})
    if not a or not b:add('*','unverified','No registered orientation evidence')
    for id in sorted(a.keys()|b.keys()):
        if id not in b:add(id,'fail','Element missing');continue
        if id not in a:add(id,'unverified','New element has no approved baseline');continue
        old,new=a[id],b[id]
        if old.get('status')!='measured' or new.get('status')!='measured':add(id,'unverified','Invalid or missing geometry anchors');continue
        if any(not old.get(k) or old.get(k)!=new.get(k) for k in ('topology_sha256','anchors_sha256')):add(id,'unverified','Topology or anchor membership changed; rebind and review');continue
        try:
            checks=[]
            if old.get('transform_parity') not in (-1,1) or new.get('transform_parity') not in (-1,1):raise ValueError('Missing transform parity')
            if old['transform_parity']!=new['transform_parity']:checks.append('Relative transform mirrored')
            if triple(old['directions'])!=triple(new['directions']):checks.append('Geometry handedness reversed')
            angles={}
            for axis in ('forward','up','right'):
                ov,nv=vec(old['directions'][axis]),vec(new['directions'][axis])
                angle=math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(ov,nv))))));angles[axis]=angle
                if angle>tolerance:checks.append(f'{axis} rotated {angle:.3f} degrees')
            add(id,'fail' if checks else 'pass',{'issues':checks,'angles_deg':angles})
        except (ValueError,TypeError,KeyError,OverflowError) as e:add(id,'unverified',str(e))
    statuses=[r['status'] for r in result['checks']]
    result['status']='fail' if 'fail' in statuses else 'unverified' if 'unverified' in statuses else 'pass'
    return result

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('inventory');q.add_argument('project');q.add_argument('--out',required=True)
    q=sub.add_parser('new-version');q.add_argument('project');q.add_argument('--reason',required=True)
    q=sub.add_parser('compare');q.add_argument('baseline');q.add_argument('current');q.add_argument('--out',required=True);q.add_argument('--tolerance-deg',type=float,default=1.)
    args=p.parse_args()
    if args.cmd=='inventory':write_new(args.out,inventory(args.project))
    elif args.cmd=='new-version':print(new_version(args.project,args.reason))
    else:
        report=compare(json.loads(Path(args.baseline).read_text()),json.loads(Path(args.current).read_text()),args.tolerance_deg)
        report['input_hashes']={'baseline':sha(Path(args.baseline)),'current':sha(Path(args.current))}
        write_new(args.out,report);print(report['status']);return 0 if report['status']=='pass' else 2
    return 0
if __name__=='__main__':raise SystemExit(main())
