"""Create correctly named copies after the user provides a non-personal account ID."""

import argparse, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--account-id", required=True)
a = p.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_-]+", a.account_id):
    raise SystemExit("Use an account ID containing only letters, digits, _ or -.")
out = ROOT / "output/submission"
out.mkdir(exist_ok=True)
name = f"説明資料_PAI最終課題_{a.account_id}.pdf"
shutil.copy2(ROOT / "output/pdf/physical_ai_so101_report.pdf", out / name)
(out / "youtube_title.txt").write_text(f"PAI最終課題_{a.account_id}\n")
print("Prepared:", out / name)
print("YouTube title:", f"PAI最終課題_{a.account_id}")
