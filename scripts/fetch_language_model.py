from huggingface_hub import HfApi, snapshot_download
from pathlib import Path
import json

repo = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
manifest = Path("model_manifest.json")
revision = (
    json.loads(manifest.read_text())["revision"]
    if manifest.exists()
    else HfApi().model_info(repo).sha
)
path = snapshot_download(
    repo_id=repo,
    revision=revision,
    local_dir="models/qwen3-4b",
    allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt", "*.md"],
)
Path("model_manifest.json").write_text(
    json.dumps(
        {
            "repo_id": repo,
            "revision": revision,
            "local_path": "models/qwen3-4b",
            "quantization": "4-bit",
            "download": str(Path(path).name),
        },
        indent=2,
    )
)
print("Downloaded", repo, revision)
