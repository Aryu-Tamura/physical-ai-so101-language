import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from arm import Arm
import mujoco,imageio,numpy as np
from PIL import Image
arm=Arm();rend=mujoco.Renderer(arm.model,height=720,width=1280)
cam=mujoco.MjvCamera();cam.lookat[:]=[.15,0,.09];cam.distance=.8;cam.azimuth=145;cam.elevation=-35
writer=imageio.get_writer('outputs/probe.mp4',fps=25)
opt=mujoco.MjvOption();opt.geomgroup[3:]=False
frames=[0]
def frame(a):
 rend.update_scene(a.data,camera=cam,scene_option=opt);im=rend.render();writer.append_data(im)
 if frames[0]%25==0:Image.fromarray(im).save(f'outputs/probe_{frames[0]:04}.jpg')
 frames[0]+=1
arm.frame_callback=frame
try:
 print(arm.pick_place());Path('outputs/probe_trace.json').write_text(json.dumps(arm.trace))
finally:writer.close();rend.close()
