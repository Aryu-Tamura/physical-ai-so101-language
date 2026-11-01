import json, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arm import Arm
from language import keyword_parse
from pipeline import decide, execute
from visuals import Recorder

cases = {
    c["id"]: c for c in json.loads((ROOT / "data/evaluation_cases.json").read_text())
}
intents = json.loads((ROOT / "outputs/evaluation/intents.json").read_text())["results"]
out = ROOT / "outputs/clips"
out.mkdir(parents=True, exist_ok=True)
specs = [
    ("basic", "T03", "llm_checked", 0, False),
    ("keyword_negation", "T05", "keyword_checked", 0, False),
    ("llm_negation", "T05", "llm_checked", 0, False),
    ("ambiguous_unchecked", "T13", "llm_unchecked", 0, False),
    ("ambiguous_checked", "T13", "llm_checked", 0, False),
    ("unreachable", "T23", "llm_checked", 0, False),
    ("grasp_failure", "T03", "llm_checked", 0.035, False),
    ("grasp_recovery", "T03", "llm_checked", 0.035, True),
]
parser = argparse.ArgumentParser()
parser.add_argument("--only")
args = parser.parse_args()
records = (
    json.loads((out / "metadata.json").read_text())
    if args.only and (out / "metadata.json").exists()
    else []
)
for name, cid, method, offset, recovery in specs:
    if args.only and name != args.only:
        continue
    c = cases[cid]
    arm = Arm(10, scenario=c["scenario"])
    intent = (
        keyword_parse(c["text"])
        if method == "keyword_checked"
        else intents[cid]["intent"]
    )
    decision = decide(arm, intent, checked=method != "llm_unchecked")
    title = {
        "basic": "01 / 日本語の指示から、つかんで置く",
        "keyword_negation": "02 / 単語だけで選ぶと、否定を取り違える",
        "llm_negation": "02 / 言語モデルは、指示の意味から対象を選ぶ",
        "ambiguous_unchecked": "03 / 同じ色が２つ：最初の候補を選ぶ方式",
        "ambiguous_checked": "03 / 同じ色が２つ：勝手に選ばず確認する",
        "unreachable": "04 / アームの届かない物は、実行前に見送る",
        "grasp_failure": "05 / 言葉が通じても、つかめるとは限らない",
        "grasp_recovery": "06 / 持ち上がったか確認し、一度だけやり直す",
    }[name]
    note = "実時間 / 評価ログの指示解釈を使用 / シミュレーション再実行"
    if offset:
        note += " / 初回の目標位置に35 mmの誤差"
    rec = Recorder(
        arm, out / f"{name}.mp4", c["text"], title=title, note=note, intent=intent
    )
    rec.hold(1)
    try:
        r = execute(arm, decision, offset=offset, recovery=recovery)
        arm.phase = (
            "配置成功"
            if r["success"]
            else (
                "どちらの赤ですか？"
                if decision["status"] == "clarify"
                else "届かないため見送り"
                if decision["status"] == "reject"
                else "物体を運べず失敗"
            )
        )
        if name == "keyword_negation":
            arm.phase = "物理成功・指示は不一致"
        if name == "ambiguous_unchecked":
            arm.phase = "配置済み・対象は未確認"
        rec.hold(3 if decision["status"] == "execute" else 7)
        rec.last.save(out / f"{name}.jpg")
    finally:
        rec.close()
    record = dict(
        name=name,
        case_id=cid,
        seed=10,
        method=method,
        offset_m=offset,
        recovery=recovery,
        intent=intent,
        decision=decision,
        result=r,
        frames=rec.frames,
        duration_s=rec.frames / 25,
    )
    records = [r for r in records if r["name"] != name]
    records.append(record)
    (out / "metadata.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2)
    )
    print(name, r, flush=True)
