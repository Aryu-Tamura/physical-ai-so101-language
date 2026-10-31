# Third-party components

## SO-101 MJCF and meshes
- Source: https://github.com/google-deepmind/mujoco_menagerie/tree/b0655057a9df2abe39ea7fc989914ba6f248301c/robotstudio_so101
- Commit: b0655057a9df2abe39ea7fc989914ba6f248301c
- Upstream: The Robot Studio / SO-ARM100, I2RT Robotics contributions; see source README.
- License: Apache-2.0; original license is assets/so101/LICENSE.
- Vendored so101.xml and meshes are unchanged. Runtime adds a tabletop scene, objects, target regions, a pinch site, lighting, timestep .002 and 50 solver iterations. Joint limits and actuator force limits remain upstream values. These are simulated parameters, not a validated identification of a particular purchased robot.

## Language model
- mlx-community/Qwen3-4B-Instruct-2507-4bit, derived from Qwen/Qwen3-4B-Instruct-2507.
- Apache-2.0, open weights; fetched separately, revision recorded in model_manifest.json.
- Local MLX inference only, no API charges and no training in this project.

## Software
MuJoCo (Apache-2.0), MLX / MLX-LM (MIT), NumPy/SciPy (BSD), Pillow (HPND), ImageIO (BSD), ReportLab (BSD), Matplotlib (PSF-compatible). Dependency versions are frozen in requirements-lock-macos.txt.

## Course material
Course PDFs/notebook are private references for assignment requirements and learning objectives. They are not included or redistributed. Project code, evaluation prompts and explanation are newly authored.
