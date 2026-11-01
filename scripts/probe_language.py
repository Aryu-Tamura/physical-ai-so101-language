import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from language import Interpreter

p = Interpreter()
cases = [
    "赤いブロックを右のトレーに置いて。",
    "青ではなく赤を左に運んで。",
    "赤いのを取って。",
    "青を右に移動しないで。",
    "緑のブロックを左に運んで。",
    "赤いブロックを右に置いて。それから青も左へ。",
]
results = []
for text in cases:
    r = {"text": text, **p.parse(text)}
    results.append(r)
    print(json.dumps(r, ensure_ascii=False), flush=True)
Path("outputs/language_development.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2)
)
