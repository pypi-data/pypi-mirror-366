import argparse
import os
import shutil
import sys
from pathlib import Path
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from diff_reviewer.reviewer import run_diff_review



CONFIG_DIR = Path.home() / ".diff_reviewer"
CONFIG_FILE = CONFIG_DIR / "config.json"

def save_config(args):
    CONFIG_DIR.mkdir(exist_ok=True)
    binary_path = shutil.which("diff-reviewer")
    if binary_path:
        binary_path = str(Path(binary_path).resolve())

    config = {
        "model_dir": str(args.model_dir),
        "model_file": str(args.model_file),
        "gdrive_model_url": args.gdrive_model_url,
        "text_context": args.text_context,
        "review_dir": str(args.review_dir),
        "prompt_prefix": args.prompt_prefix,
        "max_tokens": args.max_tokens,
        "binary_path": binary_path,
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    print(f"✅ Saved model configuration at {CONFIG_FILE}")


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"❌ Config file not found at {CONFIG_FILE}")

    config_data = json.loads(CONFIG_FILE.read_text())

    config = {
        "model_dir": Path(config_data["model_dir"]),
        "model_file": Path(config_data["model_file"]),
        "gdrive_model_url": config_data["gdrive_model_url"],
        "text_context": config_data["text_context"],
        "review_dir": Path(config_data["review_dir"]),
        "prompt_prefix": config_data["prompt_prefix"],
        "max_tokens": config_data["max_tokens"],
        "binary_path": config_data["binary_path"]
    }

    print(f"✅ Loaded model configuration from {CONFIG_FILE}")
    return config

def init_global_hook(args):
    print("🔧 Setting up global Git hook...")

    os.system("git config --global core.hooksPath ~/.git-hooks")

    hooks_dir = Path.home() / ".git-hooks"
    hooks_dir.mkdir(exist_ok=True)

    script_src = Path(__file__).parent.parent / "hooks" / "pre-commit"
    script_dst = hooks_dir / "pre-commit"

    print(f"Copying pre-commit hook from {script_src} to {script_dst}")
    shutil.copy(script_src, script_dst)
    script_dst.chmod(0o755)

    os.system(f"git config --global core.hooksPath {hooks_dir}")
    print(f"✅ Global pre-commit hook installed at {script_dst}")

    if args:
        save_config(args)
    else:
        print("⚠️ No model config provided, will use default models dir: ./models/ and model: mistral-7b-instruct-v0.2.Q4_K_M.gguf.")


def main():
    parser = argparse.ArgumentParser(description="Diff Reviewer CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init = subparsers.add_parser("init")
    init.add_argument("--model-dir", type=str, help="Path to model directory", default=Path(__file__).parent.parent / "models")
    init.add_argument("--model-file", type=str, help="Model filename", default="mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    init.add_argument("--gdrive-model-url", type=str, help="Google drive model url", default="https://drive.google.com/uc?id=1IVrCT8mzSNtfUJ5rTyDbLfcxbHzkcX2K")
    init.add_argument("--text-context", type=int, help=f"Model text context, default: {16384 // 2}", default=(16384 // 2))
    init.add_argument("--review-dir", type=str, help="Directory where the review file will be saved", default=".diff_review")
    init.add_argument("--prompt-prefix", type=str, help="Prompt prefix, default: You are a senior code reviewer. Given the diff and "
                                                        "surrounding code context, suggest improvements in code quality, logic, "
                                                        "and readability. Be precise and constructive.",
                      default="You are a senior code reviewer. Given the diff and surrounding code context, suggest improvements in code "
                              "quality, logic, and readability. "
                              f"Be precise and constructive.")
    init.add_argument("--max-tokens", type=int, help="Max tokens, default: 1024", default=1024)


    # --diff
    diff = subparsers.add_parser("diff")
    diff.add_argument("patch_file", type=Path)
    diff.add_argument("commit_id", nargs="?", default="")

    args = parser.parse_args()

    if args.command == "init":
        init_global_hook(args)
    elif args.command == "diff":
        config = load_config()
        run_diff_review(args.patch_file, args.commit_id, config)
    else:
        parser.print_help()
