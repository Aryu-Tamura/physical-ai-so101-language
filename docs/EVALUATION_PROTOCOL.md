# Evaluation protocol v1 (frozen before final inference)

## Research question
Can a free local language model interpret tabletop instructions beyond a first-keyword parser, and does scene validation prevent ambiguous or unreachable executions? Can feedback recover from a transient object-position error?

## Conditions
- keyword_checked: first explicitly mentioned color and direction, with scene checks. This is a deliberately weak, transparent baseline; not representative of all rule systems.
- llm_unchecked: same local LLM intent as full system, first match on duplicate objects, no reachability preflight. Unknown objects still cannot be resolved and are rejected. Motor limits remain enabled.
- llm_checked: local LLM + unique-reference and reachable-workspace checks.
No end-to-end VLA or learned manipulation policy is claimed. Ground-truth object attributes and coordinates come from simulation (no vision recognition).

## Frozen dataset
24 authored instructions (12 executable, 12 requiring clarification/rejection), 3 held-out scene seeds 10,11,12. Development: separate six parser instructions and physics seeds 0–4. No model fine-tuning. Prompts frozen before final evaluation; any later change requires a new protocol version, all trials rerun and previous results retained. This is a small synthetic benchmark, not a population estimate of Japanese understanding.

## Outcomes
- Decision correctness: exact expected execute/clarify/reject, plus correct object and tray for executable requests.
- End-to-end correctness: correct decision and successful physical placement for execute requests; expected non-execution for other cases.
- Physical placement: target object previously lifted above 4.5 cm, final center within 3.5 cm of goal center and height below 4 cm. Also log other-object displacement and nonfinite states.
- Report executable success and non-executable decision accuracy separately. Abstaining on every request cannot count as task success.
- First LLM latency includes warm-up; later latency reported separately. Cached intents reused across scene seeds/methods, so inference examples are 24, not 216 independent LLM samples.
- Full per-case raw model response, latency, decisions, physics outcomes and seed are saved.

## Recovery experiment
Paired with/without lift feedback, red/blue blocks, left/right goals, held-out seeds 10–12, position errors 0 or 3.5 cm. Error is transient in the first grasp target, toward the table center; second attempt uses true position again. This is an injected sensing fault, not camera-based perception, and does not model persistent calibration errors. Each arm starts from the same seed in paired conditions. At most one retry.

## Limits
Synthetic two-block world, fixed shape/mass, flat goal markers, +/-8 mm initial position randomization, ground-truth scene information, no people or real hardware. Report actual observed failures, do not equate success here with industrial readiness.

### Development prompt revision (before any held-out evaluation)
Six development instructions exposed a negation error ("青ではなく赤" -> blue) and inconsistent missing-field/stop actions with English instructions. Replaced the system prompt with Japanese rules and four development examples; retained raw v1 results in outputs/language_development_v1.json. Evaluation instructions were not used to tune this revision. The definitive system prompt is hashed in the inference cache. This is in-context prompting, not model training.
