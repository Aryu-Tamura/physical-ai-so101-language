"""Check recorded result consistency independently from the summary generator."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads((ROOT / p).read_text())


cases = read("data/evaluation_cases.json")
rows = read("outputs/evaluation/trials.json")
summary = read("outputs/evaluation/summary.json")
intents = read("outputs/evaluation/intents.json")["results"]
assert len(cases) == 24 and len(rows) == 216 and len(intents) == 24
assert len({(r["method"], r["case_id"], r["seed"]) for r in rows}) == 216
for method, s in summary.items():
    rs = [r for r in rows if r["method"] == method]
    assert len(rs) == s["n"] == 72
    assert sum(r["end_to_end_correct"] for r in rs) == s["end_to_end_correct"]
    for r in rs:
        if r["physics"]["success"]:
            final = r["physics"]["attempt_results"][-1]
            assert final["lifted"]
            assert (
                sum((final["final"][i] - final["goal"][i]) ** 2 for i in [0, 1])
                < 0.035**2
            )
            assert final["final"][2] < 0.04 and r["physics"]["finite"]
        if r["decision"]["status"] != "execute":
            assert not r["physics"]["executed"]
        if r["method"] == "llm_checked" and r["expected"]["status"] != "execute":
            assert not r["physics"]["executed"]
recovery = read("outputs/recovery/trials.json")
rs = read("outputs/recovery/summary.json")
assert len(recovery) == 48
for s in rs:
    trials = [
        r
        for r in recovery
        if r["offset_m"] == s["offset_m"] and r["recovery"] == s["recovery"]
    ]
    assert len(trials) == s["n"]
    assert sum(r["success"] for r in trials) == s["success"]
print(
    "PASS: 216 instruction trials + 48 recovery trials, saved metrics and physical success conditions agree."
)
