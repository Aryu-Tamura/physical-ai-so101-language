"""Contact-based SO-101 tabletop simulation. No attachment or object teleportation."""

from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets/so101"
COLORS = {
    "red": (0.9, 0.12, 0.15, 1),
    "blue": (0.12, 0.4, 0.95, 1),
    "yellow": (0.98, 0.7, 0.1, 1),
}


class Arm:
    def __init__(self, seed=0, friction=1.0, scenario="standard"):
        tree = ET.parse(ASSET / "so101.xml")
        root = tree.getroot()
        root.find("compiler").set("meshdir", str(ASSET / "assets"))
        root.find("option").set("timestep", ".002")
        root.find("option").set("iterations", "50")
        visual = root.find("visual")
        ET.SubElement(visual, "global", offwidth="1280", offheight="720")
        ET.SubElement(visual, "headlight", ambient=".4 .4 .4", diffuse=".7 .7 .7")
        w = root.find("worldbody")
        ET.SubElement(w, "light", pos="0 -1 2", dir="0 0 -1", diffuse=".8 .8 .8")
        ET.SubElement(
            w,
            "geom",
            name="table",
            type="plane",
            size="1 1 .02",
            rgba=".13 .18 .23 1",
            friction="1 .01 .001",
        )
        g = root.find(".//body[@name='gripper']")
        ET.SubElement(
            g,
            "site",
            name="pinch",
            pos=".007 0 -.092",
            size=".003",
            rgba="0 1 1 1",
            group="3",
        )
        rng = np.random.default_rng(seed)
        self.starts = {}
        self.objects = []
        for name, xy in [("red", (0.24, -0.07)), ("blue", (0.24, 0.07))]:
            xy = np.array(xy) + rng.uniform(-0.008, 0.008, 2)
            if scenario == "unreachable" and name == "red":
                xy[0] = 0.5
            self.starts[name] = xy
            color = "red" if scenario == "duplicate" else name
            self.objects.append({"id": name, "color": color})
            b = ET.SubElement(w, "body", name=name, pos=f"{xy[0]} {xy[1]} .016")
            ET.SubElement(b, "freejoint", name=f"{name}_free")
            ET.SubElement(
                b,
                "geom",
                name=f"{name}_geom",
                type="box",
                size=".015 .015 .015",
                mass=".025",
                rgba=" ".join(map(str, COLORS[color])),
                friction=f"{friction} .005 .0001",
                condim="6",
                solref=".01 1",
            )
        self.trays = {"left": np.array([0.15, -0.17]), "right": np.array([0.15, 0.17])}
        for name, xy in self.trays.items():
            ET.SubElement(
                w,
                "geom",
                name=f"{name}_target",
                type="box",
                pos=f"{xy[0]} {xy[1]} .001",
                size=".045 .04 .001",
                rgba=".32 .48 .48 1",
                contype="0",
                conaffinity="0",
            )
        self.model = mujoco.MjModel.from_xml_string(
            ET.tostring(root, encoding="unicode")
        )
        self.data = mujoco.MjData(self.model)
        self.ikdata = mujoco.MjData(self.model)
        self.sid = self.model.site("pinch").id
        self.bid = self.model.body("gripper").id
        self.data.qpos[:6] = [0, -0.5, 0.5, 0.9, 1.52, 1.0]
        self.data.ctrl[:] = self.data.qpos[:6]
        mujoco.mj_forward(self.model, self.data)
        self.trace = []
        self.phase = "settle"
        self.frame_callback = None
        self.advance(0.5)

    def pos(self, name):
        return self.data.body(name).xpos.copy()

    def ik(self, target, q0=None):
        q0 = self.data.qpos[:4].copy() if q0 is None else np.array(q0[:4])
        lo = self.model.jnt_range[:4, 0] + 0.00001
        hi = self.model.jnt_range[:4, 1] - 0.00001

        def residual(q):
            self.ikdata.qpos[:6] = [*q, 1.52, 1.0]
            mujoco.mj_forward(self.model, self.ikdata)
            axis = self.ikdata.xmat[self.bid].reshape(3, 3)[:, 2]
            return np.r_[
                self.ikdata.site_xpos[self.sid] - target, 0.15 * (axis - [0, 0, 1])
            ]

        sol = least_squares(
            residual,
            np.clip(q0, lo, hi),
            bounds=(lo, hi),
            xtol=1e-10,
            gtol=1e-10,
            ftol=1e-10,
            max_nfev=150,
        )
        if np.linalg.norm(residual(sol.x)[:3]) > 0.004:
            raise ValueError(f"IK unreachable {target}: {residual(sol.x)}")
        return np.r_[sol.x, 1.52]

    def advance(self, duration):
        for _ in range(round(duration / self.model.opt.timestep)):
            mujoco.mj_step(self.model, self.data)
            if round(self.data.time / self.model.opt.timestep) % 20 == 0:
                self.trace.append(
                    {
                        "t": round(self.data.time, 4),
                        "phase": self.phase,
                        "q": self.data.qpos[:6].tolist(),
                        "red": self.pos("red").tolist(),
                        "blue": self.pos("blue").tolist(),
                        "tip": self.data.site_xpos[self.sid].tolist(),
                        "contacts": int(self.data.ncon),
                    }
                )
                if self.frame_callback:
                    self.frame_callback(self)

    def move(self, target, grip=None, duration=1.4, phase="move"):
        self.phase = phase
        q = self.ik(np.array(target))
        start = self.data.ctrl.copy()
        end = np.r_[q, start[5] if grip is None else grip]
        n = round(duration / 0.02)
        for k in range(1, n + 1):
            a = k / n
            a = a * a * (3 - 2 * a)
            self.data.ctrl[:] = start + (end - start) * a
            self.advance(0.02)
        self.advance(0.2)

    def grip(self, value, duration=0.6):
        self.data.ctrl[5] = value
        self.advance(duration)

    def pick_place(self, color="red", tray="right", offset=0, stop_on_failure=False):
        start = self.pos(color)
        xy = start[:2] + [0, -np.sign(start[1]) * offset]
        goal = self.trays[tray]
        self.move([*xy, 0.075], grip=1.0, phase="approach")
        self.move([*xy, 0.018], duration=1.2, phase="descend")
        self.phase = "close"
        self.grip(-0.1, 0.8)
        self.move([*xy, 0.075], duration=1.5, phase="lift")
        lifted = bool(self.pos(color)[2] > 0.045)
        if not lifted and stop_on_failure:
            self.phase = "failure_detected"
            self.grip(1.0, 0.5)
            return {
                "lifted": False,
                "success": False,
                "final": self.pos(color).tolist(),
                "goal": goal.tolist(),
                "aborted": True,
            }
        self.move([*goal, 0.075], duration=2, phase="transfer")
        self.move([*goal, 0.025], duration=1.3, phase="lower")
        self.phase = "release"
        self.grip(1.0, 0.7)
        self.move([*goal, 0.075], duration=1.2, phase="retreat")
        self.advance(0.5)
        final = self.pos(color)
        return {
            "lifted": lifted,
            "success": bool(
                lifted and np.linalg.norm(final[:2] - goal) < 0.035 and final[2] < 0.04
            ),
            "final": final.tolist(),
            "goal": goal.tolist(),
        }
