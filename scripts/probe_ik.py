import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arm import Arm
import numpy as np

arm = Arm()
for x in [0.16, 0.20, 0.24]:
    for z in [0.018, 0.07, 0.10, 0.13]:
        try:
            print(x, z, arm.ik(np.array([x, -0.07, z])))
        except ValueError as e:
            print("FAIL", x, z)
