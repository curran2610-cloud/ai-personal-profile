import copy,importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('workflow',Path(__file__).with_name('workflow.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def snapshot():
    return {'schema':1,'project_id':'test','frame_id':'JEWELRY_FRAME','frame_world_parity':1,'errors':[],
            'elements':{'left':{'status':'measured','evidence':'evaluated_mesh_vertex_groups','topology_sha256':'abc','anchors_sha256':'def','transform_parity':1,'directions':{'forward':[1,0,0],'up':[0,0,1],'right':[0,-1,0]}}}}

class WorkflowTests(unittest.TestCase):
    def test_unchanged(self):self.assertEqual(w.compare(snapshot(),snapshot())['status'],'pass')
    def test_camera_not_orientation(self):
        a=snapshot();b=copy.deepcopy(a);b['cameras']=[{'matrix_world':'changed'}]
        self.assertEqual(w.compare(a,b)['status'],'pass')
    def test_whole_model_mirror(self):
        a=snapshot();b=snapshot();b['frame_world_parity']=-1
        self.assertEqual(w.compare(a,b)['status'],'fail')
    def test_pass_does_not_approve_baseline(self):
        r=w.compare(snapshot(),snapshot());self.assertFalse(r['baseline_approval_checked']);self.assertTrue(r['warnings'])
    def test_local_upside_down(self):
        a=snapshot();b=copy.deepcopy(a);b['elements']['left']['directions']['up']=[0,0,-1];b['elements']['left']['directions']['right']=[0,1,0]
        self.assertEqual(w.compare(a,b)['status'],'fail')
    def test_baked_mirror(self):
        a=snapshot();b=copy.deepcopy(a);b['elements']['left']['directions']['forward']=[-1,0,0]
        self.assertEqual(w.compare(a,b)['status'],'fail')
    def test_mirrored_pair_has_separate_baselines(self):
        a=snapshot();a['elements']['right']=copy.deepcopy(a['elements']['left']);a['elements']['right']['transform_parity']=-1;a['elements']['right']['directions']['right']=[0,1,0]
        self.assertEqual(w.compare(a,copy.deepcopy(a))['status'],'pass')
    def test_missing(self):
        a=snapshot();b=snapshot();b['elements']={};self.assertEqual(w.compare(a,b)['status'],'fail')
    def test_new_and_retopology_unverified(self):
        a=snapshot();b=snapshot();b['elements']['left']['topology_sha256']='new';self.assertEqual(w.compare(a,b)['status'],'unverified')
        b=snapshot();b['elements']['new']=copy.deepcopy(b['elements']['left']);self.assertEqual(w.compare(a,b)['status'],'unverified')
    def test_bad_anchor_unverified(self):
        a=snapshot();b=snapshot();b['elements']['left']['directions']['up']=[0,0,0]
        self.assertEqual(w.compare(a,b)['status'],'unverified')
    def test_missing_evidence_not_pass(self):
        a=snapshot();a['elements']={};self.assertEqual(w.compare(a,a)['status'],'unverified')
    def test_project_mismatch(self):
        a=snapshot();b=snapshot();b['project_id']='other';self.assertEqual(w.compare(a,b)['status'],'fail')
    def test_history_immutable(self):
        with tempfile.TemporaryDirectory() as t:
            one=w.new_version(t,'first');old=(one/'manifest.json').read_bytes();two=w.new_version(t,'second')
            self.assertEqual((one/'manifest.json').read_bytes(),old);self.assertEqual(two.name,'v002')
            with self.assertRaises(FileExistsError):w.write_new(one/'manifest.json',{})
    def test_inventory_does_not_claim_read(self):
        with tempfile.TemporaryDirectory() as t:
            w.write_new(Path(t)/'brief.json',{'width':7})
            items=w.inventory(t)['files'];self.assertEqual(len(items),1);self.assertEqual(items[0]['read_status'],'not_read')

if __name__=='__main__':unittest.main()
