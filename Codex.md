# Latest status — implementation and deliverables complete

- Working project: this directory. Public repository: https://github.com/Aryu-Tamura/physical-ai-so101-language
- Read START_HERE.md first; report output/pdf/physical_ai_so101_report.pdf (4 pages), video outputs/final_demo.mp4 (136 s).
- Public source b7f2eea independently cloned: all 216 instruction +48 recovery trajectories byte-identical. Same Mac/dependencies, cached evaluation LLM outputs; separate live CLI inference also succeeded.
- 7 tests passed on Mac and GitHub Linux CI. PDF all pages and video chapter frames visually inspected; video fully decoded.
- Verified full system69/72, normal tasks36/36; remaining T17 null-color clarification/rejection error is disclosed. Recovery6/12→12/12 for transient35mm error only.
- No audio/vision/real hardware. Do not claim otherwise. No ongoing simulation/training required.
- GitHub release pending creation immediately after this checkpoint; check release v1.0.0. YouTube/Omnicampus not submitted; user account ID and user review remain.
- Verification details VERIFICATION.md; per-stage scripts and data retained. Prior notes below are historical.

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

## Checkpoint 2 — language and recovery
- GitHub created and pushed: https://github.com/Aryu-Tamura/physical-ai-so101-language
- Local model downloaded: mlx-community/Qwen3-4B-Instruct-2507-4bit at 50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b. ~2.1 GB, MLX GPU inference.
- Development prompt v1 failed negation. v2 Japanese instructions + four development examples; v1 raw output retained. Final dataset not yet evaluated at this checkpoint.
- Held-out recovery trials (seeds 10–12; red/blue; left/right): 0 offset 12/12 with and without feedback. 3.5 cm transient offset: without feedback 6/12, with one retry 12/12, six retries. All details outputs/recovery/.
- Recovery uses simulator truth for re-observation. Do not claim a camera or persistent calibration correction.
- 24 held-out instructions and expected decisions frozen in data/evaluation_cases.json. Comparison: keyword+checks, LLM without uniqueness/reachability checks, LLM+checks. Three scene seeds; shared deterministic LLM intents across seeds/conditions.
- src/pipeline.py checks reachable workspace before motion, executes and logs attempts.
- Next: finish language dev run, run final evaluation, produce demo CLI and edited video/PDF, independent reproduction and artifact validation.

## Checkpoint 3 — final experiments and artifacts
- Evaluation completed: keyword_checked 48/72 (execute21/36, nonexecute27/36); llm_unchecked57/72 (36/36,21/36); llm_checked69/72 (36/36,33/36). Unwanted execution starts: 9 /12 /0. Unreachable unchecked attempts stop at IK before physical arm motion.
- Remaining failure T17: unspecified color -> LLM move/null -> guard rejects instead of clarifying. Preserved transparently, not patched using test-set answers.
- 216 instruction trials +48 recovery trials recorded; 7 focused unit tests passed. Local inference24 examples: median5.82s, min3.32,max8.59, excludes model loading.
- scripts/record_examples.py replays measured model outputs and reruns actual physics for video; src/visuals.py labels this explicitly. demo.py uses fresh live inference.
- Four-page PDF generated and all pages visually inspected; no overflow. Final MP4 136 seconds,3400frames,25fps, silent with Japanese captions. Keyword failure clip label clarified as physical success but instruction mismatch (video rebuilding).
- START_HERE.md / SUBMISSION.md / docs/LEARNING_GUIDE.md and SIM_TO_REAL.md created. Account ID, YouTube upload and Omnicampus submission remain user actions.
- Remaining: verify final video frames/decode, live CLI smoke, formatting, clean public clone reproduction, CI, final GitHub push/release, update final handoff.
- Final MP4 chapter frames visually checked (title, wrong-object action, ambiguity, failure, recovery, both charts, limitations). Caption distinguishes successful physical placement from incorrect instruction execution.
- Live demo.py path tested with fresh LLM inference (not cached); red-block placement succeeded for a negated-color instruction, producing latest_demo.mp4/json.
- Code formatted with Ruff; unit tests still pass. PDF text now also states 69/72 outside the plotted image so machine-readable validation can check it.
