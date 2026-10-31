import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from arm import Arm
import numpy as np
arm=Arm()
for x in [.16,.20,.24]:
 for z in [.018,.07,.10,.13]:
  try: print(x,z,arm.ik(np.array([x,-.07,z])))
  except ValueError as e: print('FAIL',x,z)
