"""Execution supervisor: preflight, feedback, bounded retry and observable outcomes."""
import time
import numpy as np
from language import ground

def decide(arm,intent,checked=True):
 decision=ground(intent,arm.objects,checked=checked)
 if checked and decision['status']=='execute':
  p=arm.pos(decision['object_id']);goal=arm.trays[decision['destination']]
  try:
   for target in [[*p[:2],.075],[*p[:2],.018],[*goal,.075],[*goal,.025]]:arm.ik(np.array(target))
  except ValueError:
   return {'status':'reject','reason':'outside_workspace'}
 return decision

def execute(arm,decision,offset=0,recovery=False):
 if decision['status']!='execute':return {'executed':False,'success':False,'attempts':0,'sim_duration_s':0.0,'wall_duration_s':0.0}
 obj=decision['object_id'];other='blue' if obj=='red' else 'red'
 initial_other=arm.pos(other);t=arm.data.time;start=time.perf_counter();attempts=[]
 try:
  attempts.append(arm.pick_place(obj,decision['destination'],offset=offset,stop_on_failure=recovery))
  if recovery and not attempts[-1]['lifted']:
   attempts.append(arm.pick_place(obj,decision['destination'],offset=0,stop_on_failure=True))
  success=attempts[-1]['success'];error=None
 except ValueError as e:success=False;error=str(e)
 finite=bool(np.all(np.isfinite(arm.data.qpos)) and np.all(np.isfinite(arm.data.qvel)))
 return {'executed':True,'success':bool(success and finite),'attempts':len(attempts),'attempt_results':attempts,'error':error,'finite':finite,'other_displacement_m':float(np.linalg.norm(arm.pos(other)-initial_other)),'sim_duration_s':float(arm.data.time-t),'wall_duration_s':time.perf_counter()-start}
