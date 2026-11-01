import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from arm import Arm
from language import ground
from pipeline import decide,execute

class GroundingTests(unittest.TestCase):
 def test_duplicate_object_is_not_arbitrarily_selected(self):
  a=Arm(scenario='duplicate');q=a.data.qpos.copy()
  decision=decide(a,{'action':'move','color':'red','destination':'right'})
  self.assertEqual(decision['status'],'clarify');self.assertFalse(execute(a,decision)['executed']);np.testing.assert_array_equal(q,a.data.qpos)
 def test_nonexistent_object_is_rejected(self):
  a=Arm();d=decide(a,{'action':'move','color':'green','destination':'left'});self.assertEqual(d['status'],'reject')
 def test_unreachable_target_preflight_does_not_move_arm(self):
  a=Arm(scenario='unreachable');q=a.data.qpos.copy();t=a.data.time
  d=decide(a,{'action':'move','color':'red','destination':'left'});self.assertEqual(d['reason'],'outside_workspace');self.assertEqual(a.data.time,t);np.testing.assert_array_equal(q,a.data.qpos)
 def test_missing_destination_requests_clarification(self):
  a=Arm();self.assertEqual(decide(a,{'action':'move','color':'red','destination':None})['status'],'clarify')
 def test_reject_does_not_issue_motion(self):
  a=Arm();q=a.data.qpos.copy();d=decide(a,{'action':'reject','color':'red','destination':'right'});self.assertFalse(execute(a,d)['executed']);np.testing.assert_array_equal(q,a.data.qpos)

class PhysicsTests(unittest.TestCase):
 def test_contact_pick_place_and_no_artificial_attachments(self):
  a=Arm(3);self.assertEqual(a.model.neq,0);self.assertEqual(a.model.nmocap,0)
  r=execute(a,{'status':'execute','object_id':'blue','destination':'left'});self.assertTrue(r['success']);self.assertLess(r['other_displacement_m'],.001);self.assertTrue(any(s['blue'][2]>.045 for s in a.trace))
  self.assertTrue(np.all(a.data.xfrc_applied==0));self.assertTrue(np.all(a.data.qfrc_applied==0))
 def test_transient_error_fails_then_feedback_recovers(self):
  d={'status':'execute','object_id':'red','destination':'right'}
  bad=execute(Arm(3),d,offset=.035,recovery=False);good=execute(Arm(3),d,offset=.035,recovery=True)
  self.assertFalse(bad['success']);self.assertTrue(good['success']);self.assertEqual(good['attempts'],2)

if __name__=='__main__':unittest.main(verbosity=2)
