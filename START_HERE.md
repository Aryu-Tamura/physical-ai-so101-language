# 朝に確認する順番

1. **動画を見る（2分16秒）**：`outputs/final_demo.mp4`。日本語字幕、音声なし、シミュレーション部分は実時間。
2. **PDFを読む（4ページ）**：`output/pdf/physical_ai_so101_report.pdf`。
3. **実際に指示する**：このフォルダをTerminalで開き、次を実行。

```bash
.venv/bin/python demo.py --instruction '青ではなく赤を左のトレーに置いて。' --video
open outputs/latest_demo.mp4
```

4. 余裕があれば `docs/LEARNING_GUIDE.md` の例を3つ試す。
5. 提出前に `SUBMISSION.md` を確認する。

## 主な結果

- 正常な作業：LLM＋確認 36/36、単語方式21/36。
- 確認・拒否が必要な場面：LLM＋確認 33/36。色未指定で「確認」でなく「拒否」する失敗が残る。
- 35mmの一時的位置誤差：再試行なし6/12、一度の再試行あり12/12。
- 24指示×3配置×3方式＝216試行、誤差比較48試行。LLM推論自体は評価用24件。
- シミュレータ内部の物体情報を使っている。実カメラ、音声認識、実機は未検証。

## 公開先

https://github.com/Aryu-Tamura/physical-ai-so101-language

## まだ必要なこと

本人の内容確認、OmnicampusのアカウントIDによるファイル名・動画タイトル設定、YouTube投稿、Omnicampus提出。提出締切は2026年11月2日10:00。成果物の作成完了と提出完了は別です。
