import sys, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arm import Arm
from pipeline import execute

p = argparse.ArgumentParser()
p.add_argument("--output", default="outputs/recovery")
args = p.parse_args()
out = ROOT / args.output
out.mkdir(parents=True, exist_ok=True)
(out / "traces").mkdir(exist_ok=True)
rows = []
for offset in [0, 0.035]:
    for recovery in [False, True]:
        for seed in [10, 11, 12]:
            for color in ["red", "blue"]:
                for tray in ["left", "right"]:
                    arm = Arm(seed)
                    decision = {
                        "status": "execute",
                        "object_id": color,
                        "destination": tray,
                    }
                    r = execute(arm, decision, offset=offset, recovery=recovery)
                    name = f"{offset}_{recovery}_{seed}_{color}_{tray}"
                    rows.append(
                        dict(
                            id=name,
                            offset_m=offset,
                            recovery=recovery,
                            seed=seed,
                            color=color,
                            tray=tray,
                            **r,
                        )
                    )
                    (out / "traces" / f"{name}.json").write_text(
                        json.dumps(arm.trace, separators=(",", ":"))
                    )
                    (out / "trials.json").write_text(json.dumps(rows, indent=2))
        print(offset, recovery, "completed", flush=True)
summary = []
for offset in [0, 0.035]:
    for recovery in [False, True]:
        rs = [r for r in rows if r["offset_m"] == offset and r["recovery"] == recovery]
        summary.append(
            {
                "offset_m": offset,
                "recovery": recovery,
                "n": len(rs),
                "success": sum(r["success"] for r in rs),
                "retries": sum(r["attempts"] > 1 for r in rs),
            }
        )
(out / "summary.json").write_text(json.dumps(summary, indent=2))
print(summary)
