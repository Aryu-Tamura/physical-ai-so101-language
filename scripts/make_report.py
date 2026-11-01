"""Build the report from saved measurements; no result values are invented."""

import json, sys, os, platform, hashlib
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "outputs/.matplotlib"))
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib.pagesizes import A4

out = ROOT / "outputs"
pdfdir = ROOT / "output/pdf"
pdfdir.mkdir(parents=True, exist_ok=True)
s = json.loads((out / "evaluation/summary.json").read_text())
rs = json.loads((out / "recovery/summary.json").read_text())
ints = json.loads((out / "evaluation/intents.json").read_text())["results"]
lat = [x["latency_s"] for x in ints.values()]
methods = ["keyword_checked", "llm_unchecked", "llm_checked"]
names = ["First keyword + checks", "LLM without scene checks", "LLM + scene checks"]
cols = ["#bb7950", "#508ba3", "#167f75"]
fig, ax = plt.subplots(figsize=(8.8, 3.3), layout="constrained")
v = [s[m]["end_to_end_correct"] for m in methods]
ax.barh(names, v, color=cols)
ax.set_xlim(0, 80)
ax.set_xlabel("Correct end-to-end outcomes / 72 scene trials")
ax.invert_yaxis()
ax.spines[["top", "right"]].set_visible(False)
for i, n in enumerate(v):
    ax.text(n + 0.8, i, f"{n}/72 ({100 * n / 72:.1f}%)", va="center", fontsize=10)
fig.savefig(out / "comparison.png", dpi=180)
plt.close(fig)
fig, ax = plt.subplots(figsize=(8.8, 3), layout="constrained")
ax.bar(
    ["No retry", "Observe lift + one retry"],
    [rs[2]["success"], rs[3]["success"]],
    color=[cols[0], cols[2]],
)
ax.set_ylim(0, 14)
ax.set_ylabel("Successful placements / 12")
ax.set_title("Injected transient position error: 35 mm")
ax.spines[["top", "right"]].set_visible(False)
for i, n in enumerate([rs[2]["success"], rs[3]["success"]]):
    ax.text(i, n + 0.2, f"{n}/12", ha="center")
fig.savefig(out / "recovery_comparison.png", dpi=180)
plt.close(fig)
font = os.environ.get(
    "PAI_PDF_FONT", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
)
pdfmetrics.registerFont(TTFont("JP", font))
ink = colors.HexColor("#1b3040")
accent = colors.HexColor("#12796c")
body = ParagraphStyle(
    "Body",
    fontName="JP",
    fontSize=9.2,
    leading=14.2,
    spaceAfter=7,
    textColor=ink,
    wordWrap="CJK",
)
small = ParagraphStyle("Small", parent=body, fontSize=7.8, leading=11.5)
h1 = ParagraphStyle(
    "Title", parent=body, fontSize=22, leading=31, spaceAfter=13, textColor=accent
)
h2 = ParagraphStyle(
    "Heading",
    parent=body,
    fontSize=12,
    leading=18,
    spaceBefore=8,
    spaceAfter=6,
    textColor=accent,
)
story = []
markdown = []


def p(text, style=body):
    story.append(Paragraph(escape(text), style))
    markdown.append(text + "\n")


def h(text):
    p(text, h2)


def table(rows, widths):
    t = Table(
        [[Paragraph(escape(str(c)), small) for c in row] for row in rows],
        colWidths=widths,
    )
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3f1ee")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, accent),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#d0dce2")),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 7))
    markdown.extend([" | ".join(map(str, r)) for r in rows])
    markdown.append("")


def img(path, w, hh):
    story.append(Image(str(path), width=w, height=hh))


def page():
    story.append(PageBreak())
    markdown.append("\n---\n")


p("言葉が通じても、\nつかめるとは限らない".replace("\n", " "), h1)
p("SO-101による日本語指示・物理操作・失敗回復の検証", h2)
p("Physical AI 応用編1 最終課題 / 2026年11月1日", small)
img(out / "clips/basic.jpg", 495, 278.4)
h("1. 目的と問い")
p(
    "個人でも導入を検討できる小型アームを、工作・軽作業の卓上アシスタントとして使いたい。そこで「色付きブロックを指定の置き場へ運ぶ」作業を題材に、言葉の意味を理解することと、物理的な作業を完了することの違いを調べた。"
)
p(
    "問いは、①否定や言い直しを含む指示を解釈できるか、②対象が曖昧・不在・到達不能な場合に実行を見送れるか、③つかみ損ねに気づいて再試行すると成功率が改善するか、の3点である。"
)
h("AIと制御の役割")
p(
    "AIはQwen3-4B-Instruct-2507の4bit版によるテキスト推論。出力は対象色・行き先・操作のJSON。物体の存在確認、逆運動学、関節位置制御、成功判定は明示的なプログラムである。モデル学習・音声認識・画像認識は実施していない。"
)
page()
p("実装と再現できる評価", h1)
h("2. システム構成")
p(
    "日本語テキスト → ローカルLLM → 構造化指示 → 対象の一意性・到達可能性を確認 → 逆運動学 → 関節目標角 → MuJoCoの接触・重力・摩擦 → 結果を記録。"
)
p(
    "SO-101の公開MJCFとメッシュを使用し、関節可動域・アクチュエータの力制限は公開モデルの値を維持した。物体を持ち上げるための固定拘束や、実行中に物体位置を書き換える操作はない。対象の色と座標はシミュレータ内部情報を使用する。左右の置き場は平面の目標領域であり、実物の箱ではない。"
)
p(
    "最初の高い持ち上げ軌道は、下向きの指先姿勢を保ったまま到達できなかった。作業範囲を絞り、移動時の指先高さを7.5cmに変更した。開発用の20試行で把持・配置を確認してから評価へ進んだ。"
)
h("3. 評価設計")
table(
    [
        ["項目", "条件"],
        [
            "言語・操作評価",
            "24指示（実行12、確認・拒否12）×配置seed 10/11/12 ×3方式＝216試行",
        ],
        ["比較方式", "最初の色・方向の単語＋確認 / LLM＋確認なし / LLM＋確認あり"],
        ["失敗回復評価", "誤差0または35mm ×再試行なし/あり ×2色×2行き先×3seed＝48試行"],
        [
            "物理成功",
            "対象が高さ4.5cmを超えて持ち上がり、最後に目標中心から3.5cm以内かつ高さ4cm未満",
        ],
        [
            "再現性",
            "モデルrevision、依存版、プロンプトとデータのハッシュ、各試行の出力・座標・seedを保存",
        ],
    ],
    [100, 395],
)
p(
    "配置の乱数は初期位置の各軸±8mm。LLMは24指示を各1回推論し、同じ結果を3配置と比較方式で共有した。72試行は72種類の独立した日本語例ではない。開発用6指示で設定を調整した後、評価用24指示では変更していない。",
    small,
)
h("実行環境・RoboOps")
p(
    "Apple M3 / 16GB、Python 3.12、MuJoCo 3.2.7、MLX-LM 0.32.2。無料のローカル推論を使用した。第2回の「管理・検証・自動化」を、条件固定・失敗例の保存・評価スクリプト・自動テストに反映した。音声認識を外すことで、聞き間違いと操作失敗を切り分けた。"
)
page()
p("結果：理解・確認・物理を分ける", h1)
img(out / "comparison.png", 495, 185.6)
table(
    [
        ["方式", "正常な作業を完了", "確認・拒否が適切", "不要な実行開始"],
        [
            "単語＋確認",
            f"{s[methods[0]]['executable_success']}/36",
            f"{s[methods[0]]['non_executable_correct']}/36",
            s[methods[0]]["unwanted_executions"],
        ],
        [
            "LLM・確認なし",
            f"{s[methods[1]]['executable_success']}/36",
            f"{s[methods[1]]['non_executable_correct']}/36",
            s[methods[1]]["unwanted_executions"],
        ],
        [
            "LLM＋確認",
            f"{s[methods[2]]['executable_success']}/36",
            f"{s[methods[2]]['non_executable_correct']}/36",
            s[methods[2]]["unwanted_executions"],
        ],
    ],
    [145, 115, 115, 120],
)
p(
    "単語方式は否定・訂正を含む5指示で対象や行き先を誤った。LLMは実行可能な12指示を正しく解釈したが、確認なしでは同色2個から勝手に選ぶ、届かない物への実行を試みるという問題が生じた。到達不能では逆運動学で停止し、実際の腕の移動には進んでいない。"
)
p(
    "LLM＋確認は69/72が期待どおりだったが、失敗も残った。「ブロックを左へ」の色未指定に対し、モデルがmove・color=nullを出し、後段が確認要求ではなく不存在として拒否した（T17、3配置）。不完全出力を動作へ通さなかった点と、対話として正しく確認できなかった点を区別する。"
)
img(out / "recovery_comparison.png", 495, 168.75)
p(
    "初回の把持目標に35mmの誤差を入れると、再試行なしは6/12成功。持ち上げを確認し、一度再観測してやり直すと12/12となった。誤差なしは両方式12/12。誤差ありの平均シミュレーション時間は11.8秒から14.8秒へ増えた。",
    small,
)
page()
p("考察・限界・再現方法", h1)
h("4. 何が分かったか")
p(
    "言語モデルの理解力と、ロボットに実行させてよいかの判断は別の問題である。また、正しく対象を選んでも、位置誤差があればつかめない。言語・実行前確認・物理結果のログを分けることで、改善すべき場所を特定できた。"
)
p(
    "開発時には英語のシステム指示で「青ではなく赤」を青と解釈した。日本語の規則と開発例を追加すると改善した。変更前の出力も保存しており、結果だけでなく試行錯誤を確認できる。"
)
p(
    f"LLM推論時間は24指示で中央値{np.median(lat):.2f}秒、範囲{min(lat):.2f}〜{max(lat):.2f}秒（初回を含む、モデル読込は除外）。この値はテキスト解釈の処理時間であり、音声遅延や実機応答時間ではない。今回、遅延を変化させる比較実験は行っていない。"
)
h("5. 結果の限界")
p(
    "小規模な人工指示セットと2個の同形ブロックを使う限定的な実験である。成功率を日本語全般・未知物体・実機の能力へ一般化できない。単語方式は意図的に単純な比較対象であり、すべてのルールベース手法より優れることを示していない。"
)
p(
    "再試行では2回目に正しい位置が得られる。継続する校正誤差やカメラの遮蔽には対応していない。実機、実カメラ、音声、産業現場の安全性は未検証。持ち上げ判定にもシミュレータの真の物体高さを用いている。色未指定の確認処理と、現実の観測誤差を含む評価は今後の課題である。"
)
h("6. 再現とAI支援")
p(
    "READMEの手順で環境を作り、demo.pyで新しい指示を入力できる。run_evaluation.pyで言語・物理評価、run_recovery.pyで誤差比較を再実行する。記録済み推論を利用する場合は、推論の再実行とは区別する。GitHubにコード、評価入力、モデル出力、数値ログ、出典を公開する。"
)
p(
    "テーマ・用途・制約は受講者が設定し、実装・評価の自動化・資料作成にはCodexの支援を用いた。講義資料自体は公開物へ含めていない。"
)
h("出典・公開コード")
for line in [
    "SO-101モデル: github.com/google-deepmind/mujoco_menagerie （commit b0655057…、Apache-2.0）",
    "言語モデル: huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit （revision 50d42775…）",
    "推論: github.com/ml-explore/mlx-lm / シミュレータ: mujoco.org",
    "参考: anthropic.com/research/claude-plays-robotics （操作方法を分けて評価する発想）",
    "成果物: github.com/Aryu-Tamura/physical-ai-so101-language",
]:
    p(line, small)


def footer(canvas, doc):
    canvas.setFont("JP", 8)
    canvas.setFillColor(ink)
    canvas.drawString(42, 24, "Physical AI / SO-101 text-command experiment")
    canvas.drawRightString(A4[0] - 42, 24, str(doc.page))


path = pdfdir / "physical_ai_so101_report.pdf"
doc = SimpleDocTemplate(
    str(path),
    pagesize=A4,
    leftMargin=42,
    rightMargin=42,
    topMargin=36,
    bottomMargin=40,
    title="言葉が通じても、つかめるとは限らない",
    author="",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
(ROOT / "REPORT.md").write_text(
    "# 言葉が通じても、つかめるとは限らない\n\n" + "\n".join(markdown)
)
print(path)
