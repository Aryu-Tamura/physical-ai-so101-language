import json, sys
from pathlib import Path
import numpy as np, imageio
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from visuals import card, FONTS, BG, FG, ACCENT, MUTED

out = ROOT / "outputs"
writer = imageio.get_writer(
    str(out / "final_demo.mp4"), fps=25, quality=8, macro_block_size=1
)
frames = 0
chapters = []


def emit(im):
    global frames
    writer.append_data(np.asarray(im))
    frames += 1


def still(title, lines, seconds):
    chapters.append({"title": title, "start_s": frames / 25})
    im = card(title, lines)
    for _ in range(round(seconds * 25)):
        emit(im)


def clip(name, limit=None):
    chapters.append({"clip": name, "start_s": frames / 25})
    reader = imageio.get_reader(out / "clips" / f"{name}.mp4")
    for i, im in enumerate(reader):
        if limit is not None and i >= limit * 25:
            break
        emit(im)
    reader.close()


def chart(title, path, caption, seconds):
    chapters.append({"title": title, "start_s": frames / 25})
    im = card(title, [])
    chart = Image.open(path).convert("RGB")
    chart.thumbnail((1120, 410))
    im.paste(chart, ((1280 - chart.width) // 2, 220))
    d = ImageDraw.Draw(im)
    d.text((52, 657), caption, font=FONTS[20], fill=MUTED)
    for _ in range(round(seconds * 25)):
        emit(im)


try:
    still(
        "言葉が通じても、つかめるとは限らない",
        [
            "日本語で頼める、卓上ロボットアームを作る。",
            "SO-101 × ローカル言語モデル × MuJoCo",
            "実機なし・テキスト指示・無料のローカル推論",
        ],
        7,
    )
    clip("basic")
    still(
        "「赤ではなく、青」を理解できる？",
        [
            "同じ指示を、単語だけで選ぶ方式と言語モデルで比較。",
            "アームの制御・物体の配置は共通。",
        ],
        5,
    )
    clip("keyword_negation")
    clip("llm_negation")
    clip("ambiguous_checked")
    still(
        "言葉の解釈が正しくても、物理で失敗する",
        [
            "初回の把持目標に、35 mmの位置誤差を加える。",
            "物体の座標を直接動かさず、接触でつかむ。",
        ],
        5,
    )
    clip("grasp_failure")
    clip("grasp_recovery")
    chart(
        "位置誤差があるとき：結果確認と再試行の効果",
        out / "recovery_comparison.png",
        "同じ12条件で比較。再試行は1回まで。2回目は正しい位置を取得できる前提。",
        8,
    )
    chart(
        "日本語24指示 × 3配置：期待どおりに判断・実行できたか",
        out / "comparison.png",
        "LLM＋確認でも69/72。色の未指定を「確認」でなく「拒否」にする失敗が残った。",
        9,
    )
    still(
        "理解すること、実行できること、確かめること",
        [
            "AI：言葉の解釈。制御：逆運動学と関節位置制御。",
            "物体情報はシミュレータ内部から取得。実機・画像認識は未検証。",
            "コード・失敗例・数値ログ・再現手順を公開。",
        ],
        9,
    )
finally:
    writer.close()
metadata = {
    "fps": 25,
    "frames": frames,
    "duration_s": frames / 25,
    "audio": False,
    "playback_speed": 1,
    "inference": "Recorded real LLM outputs reused; physical simulation rerun",
    "chapters": chapters,
}
(out / "final_demo_metadata.json").write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2)
)
print(metadata)
