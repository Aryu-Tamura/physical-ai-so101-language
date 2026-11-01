"""Run real local LLM inference and contact-based SO-101 manipulation."""

import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from language import Interpreter
from arm import Arm
from pipeline import decide, execute


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instruction", default="青ではなく赤を左のトレーに置いて。")
    p.add_argument(
        "--scenario",
        choices=["standard", "duplicate", "unreachable"],
        default="standard",
    )
    p.add_argument("--seed", type=int, default=10)
    p.add_argument("--video", action="store_true")
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--offset", type=float, default=0)
    p.add_argument("--retry", action="store_true")
    args = p.parse_args()
    print("ローカル言語モデルを読み込みます。外部APIへの送信はありません。", flush=True)
    model = Interpreter()
    while True:
        text = input("指示（空欄で終了）> ") if args.interactive else args.instruction
        if not text:
            break
        started = time.perf_counter()
        result = model.parse(text)
        arm = Arm(args.seed, scenario=args.scenario)
        decision = decide(arm, result["intent"])
        delay = time.perf_counter() - started
        print(
            json.dumps(
                {
                    "text": text,
                    **result,
                    "decision": decision,
                    "request_to_ready_s": delay,
                },
                ensure_ascii=False,
                indent=2,
            ),
            flush=True,
        )
        recorder = None
        if args.video:
            from visuals import Recorder

            recorder = Recorder(
                arm, ROOT / "outputs/latest_demo.mp4", text, intent=result["intent"]
            )
            recorder.hold(1)
        try:
            physics = execute(arm, decision, offset=args.offset, recovery=args.retry)
            if recorder:
                arm.phase = (
                    "配置成功"
                    if physics["success"]
                    else (
                        "確認が必要"
                        if decision["status"] == "clarify"
                        else "実行見送り"
                        if decision["status"] == "reject"
                        else "配置失敗"
                    )
                )
                recorder.hold(2)
                recorder.last.save(ROOT / "outputs/latest_demo.jpg")
        finally:
            if recorder:
                recorder.close()
        record = dict(
            text=text,
            seed=args.seed,
            scenario=args.scenario,
            **result,
            decision=decision,
            physics=physics,
            request_to_ready_s=delay,
        )
        (ROOT / "outputs").mkdir(exist_ok=True)
        (ROOT / "outputs/latest_demo.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2)
        )
        print(json.dumps(physics, ensure_ascii=False, indent=2))
        if not args.interactive:
            break


if __name__ == "__main__":
    main()
