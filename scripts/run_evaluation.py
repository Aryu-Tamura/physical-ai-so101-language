import argparse, json, sys, hashlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arm import Arm
from language import Interpreter, keyword_parse, SYSTEM
from pipeline import decide, execute

p = argparse.ArgumentParser()
p.add_argument("--reuse-intents", action="store_true")
p.add_argument("--output", default="outputs/evaluation")
args = p.parse_args()
out = ROOT / args.output
out.mkdir(parents=True, exist_ok=True)
cases = json.loads((ROOT / "data/evaluation_cases.json").read_text())
sha = hashlib.sha256(SYSTEM.encode()).hexdigest()
cache = out / "intents.json"
if args.reuse_intents:
    payload = json.loads(cache.read_text())
    assert payload["prompt_sha256"] == sha
    assert (
        payload["dataset_sha256"]
        == hashlib.sha256(
            (ROOT / "data/evaluation_cases.json").read_bytes()
        ).hexdigest()
    )
    intents = payload["results"]
else:
    model = Interpreter()
    intents = {}
    for c in cases:
        intents[c["id"]] = model.parse(c["text"])
        print(c["id"], intents[c["id"]], flush=True)
        cache.write_text(
            json.dumps(
                {
                    "prompt_sha256": sha,
                    "dataset_sha256": hashlib.sha256(
                        (ROOT / "data/evaluation_cases.json").read_bytes()
                    ).hexdigest(),
                    "results": intents,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    del model
methods = ["keyword_checked", "llm_unchecked", "llm_checked"]
rows = []
for method in methods:
    for c in cases:
        for seed in [10, 11, 12]:
            arm = Arm(seed, scenario=c["scenario"])
            intent = (
                keyword_parse(c["text"])
                if method == "keyword_checked"
                else intents[c["id"]]["intent"]
            )
            decision = decide(arm, intent, checked=method != "llm_unchecked")
            expected = c["expected"]
            correct = decision["status"] == expected["status"]
            if expected["status"] == "execute":
                correct = (
                    correct
                    and decision.get("object_id") == expected["object_id"]
                    and decision.get("destination") == expected["destination"]
                )
            physics = execute(arm, decision)
            result = dict(
                method=method,
                case_id=c["id"],
                category=c["category"],
                seed=seed,
                text=c["text"],
                scenario=c["scenario"],
                expected=expected,
                intent=intent,
                decision=decision,
                decision_correct=correct,
                end_to_end_correct=bool(
                    correct
                    and (
                        physics["success"]
                        if expected["status"] == "execute"
                        else not physics["executed"]
                    )
                ),
                physics=physics,
            )
            rows.append(result)
            trace_dir = out / "traces"
            trace_dir.mkdir(exist_ok=True)
            (trace_dir / f"{method}_{c['id']}_{seed}.json").write_text(
                json.dumps(arm.trace, separators=(",", ":"))
            )
            (out / "trials.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=2)
            )
        print(
            method,
            c["id"],
            rows[-1]["decision"],
            rows[-1]["end_to_end_correct"],
            flush=True,
        )
summary = {}
for method in methods:
    rs = [r for r in rows if r["method"] == method]
    valid = [r for r in rs if r["expected"]["status"] == "execute"]
    invalid = [r for r in rs if r["expected"]["status"] != "execute"]
    summary[method] = {
        "n": len(rs),
        "decision_correct": sum(r["decision_correct"] for r in rs),
        "end_to_end_correct": sum(r["end_to_end_correct"] for r in rs),
        "executable_n": len(valid),
        "executable_success": sum(r["end_to_end_correct"] for r in valid),
        "non_executable_n": len(invalid),
        "non_executable_correct": sum(r["end_to_end_correct"] for r in invalid),
        "unwanted_executions": sum(r["physics"]["executed"] for r in invalid),
    }
(out / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
