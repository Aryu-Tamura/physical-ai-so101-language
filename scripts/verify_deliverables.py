import json, hashlib
from pathlib import Path
from pypdf import PdfReader
from imageio_ffmpeg import count_frames_and_secs

ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT / "output/pdf/physical_ai_so101_report.pdf"
video = ROOT / "outputs/final_demo.mp4"
r = PdfReader(pdf)
assert len(r.pages) == 4
text = "\n".join(p.extract_text() for p in r.pages)
for required in ["69/72", "36/36", "6/12", "12/12", "音声", "未検証"]:
    assert required in text, required
assert "/Users/" not in text
metadata = json.loads((ROOT / "outputs/final_demo_metadata.json").read_text())
frames, seconds = count_frames_and_secs(str(video))
assert frames == metadata["frames"] == 3400
assert 60 <= seconds <= 180
assert abs(seconds - metadata["duration_s"]) < 0.1
for f in [
    "README.md",
    "REPORT.md",
    "Codex.md",
    "docs/EVALUATION_PROTOCOL.md",
    "docs/SIM_TO_REAL.md",
    "docs/LEARNING_GUIDE.md",
    "model_manifest.json",
    "THIRD_PARTY.md",
]:
    assert (ROOT / f).is_file()
checks = {
    "pdf_pages": len(r.pages),
    "video_frames": frames,
    "video_seconds": seconds,
    "video_audio": False,
    "files": {
        str(p.relative_to(ROOT)): {
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in [pdf, video]
    },
}
(ROOT / "outputs/deliverable_checks.json").write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
