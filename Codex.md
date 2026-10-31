# Text-command SO-101 experiment — persistent handoff

## User authorization / scope
- 2026-11-01: User approved implementation through verified results, video, report and reproducible code, in this directory.
- Text instructions are primary. Audio recognition excluded: isolate language grounding and physical manipulation failures.
- Mac Apple M3 / 16 GB; no paid GPU/API. Public GitHub authorized in conversation. Do not publish course PDFs, personal identifiers, or credentials.
- Final deadline confirmed from user-supplied 10/19 PDF: 2026-11-02 10:00 JST. Deliver PDF, public GitHub URL, 1–3 minute MP4 for YouTube (at least unlisted). Upload/submission status must be explicit.

## Objective / scope
A tabletop arm follows Japanese text instructions to move colored blocks to trays. Investigate paraphrases, negation, ambiguity, unavailable objects and manipulation failures. Language model inference is real, not simulated or substituted by a hardcoded parser. Physics uses contact/gravity; never teleport or weld objects to report a grasp.

## Strategy
1. Native MuJoCo SO-101 model and contact pick/place baseline.
2. Local small language model produces structured intent; deterministic checks verify references/ranges.
3. Seeded evaluation separates language correctness, physical success and clarification/refusal.
4. Record per-step data, model revision, environment versions; produce report/video from measured results.
5. Keep real-hardware migration instructions separate.

## Initial findings
- Empty target folder confirmed; no ~/AGENTS.md.
- Prior project ~/02_PhysicalーAI-最終課題 has working MuJoCo 3.2.7, Python 3.12, reporting/video tools; read-only reference.
- isaka1022/so101-sim2real README explicitly says demo does NOT demonstrate successful lifting and overhead IK is not supported. Prefer Menagerie SO-101 asset + own controller rather than assuming its grasp works.
- Course PDFs successfully read via direct paths under OneDrive/02_Physical AI講座 despite directory-list access denial. Course emphasizes RoboOps: manage, validate, automate. Extracted text in /private/tmp/pai_lecture_*.txt and pai_notebook.txt (temporary, not public deliverables).

## Current state
Planning checkpoint. No completed simulations or claimed results yet.

## Next steps
Fetch pinned SO-101 assets; create isolated environment; inspect joint/gripper geometry; prove contact-based pick/place. Evaluate local model availability. Commit and push at validated milestones.

## Checkpoint 1 — contact manipulation validated
- Native MuJoCo 3.2.7 SO-101 assets vendored with Apache license. Exact Menagerie revision in THIRD_PARTY.md.
- src/arm.py uses inverse kinematics + limited joint position actuators and contact friction. No weld/equality attachments, no object pose assignment during simulation.
- Development trial seeds 0–4 × red/blue × left/right: 20/20 lifts and placements succeeded. Results outputs/physics_development.json.
- Initial vertical travel at 13–14 cm was unreachable with fixed downward gripper orientation. Reduced travel tip height to 7.5 cm; documented as bounded workspace, not all-position capability.
- Left/right defined from human viewpoint facing the robot (+x side): left=y negative, right=y positive. Tray graphics are flat goal markers, not physical bins.
- Probe video visually inspected at approach/lift/place; matching object motion verified numerically.
- Language model download still in progress. Next: semantic parser and held-out cases; then integrated evaluation.
