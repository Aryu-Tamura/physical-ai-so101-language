from pathlib import Path
import mujoco, numpy as np

m = mujoco.MjModel.from_xml_path("assets/so101/so101.xml")
d = mujoco.MjData(m)
for q in [np.zeros(6), [0, 0, 0.4732, 1.17718, 1.58438, 0.727665]]:
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    print(
        "q",
        q,
        "tip",
        d.site("gripperframe").xpos,
        "gripper",
        d.body("gripper").xpos,
        "R",
        d.body("gripper").xmat.reshape(3, 3),
    )
