from llama_cpp import Llama
from pathlib import Path
import gdown
import time


def parse_diff_file(diff_path: Path):
    file_diffs = {}
    current_file = None
    current_chunk = []

    for line in diff_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("+++ b/"):
            if current_file and current_chunk:
                file_diffs[current_file] = "\n".join(current_chunk)
                current_chunk = []

            current_file = line[6:]
        elif current_file:
            current_chunk.append(line)

    if current_file and current_chunk:
        file_diffs[current_file] = "\n".join(current_chunk)

    return file_diffs

def run_diff_review(diff_path: Path, commit_id: str, config: dict):
    start_time = time.time()

    model_dir = Path(config.get("model_dir"))
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = config.get("model_file")
    model_path = model_dir / model_file

    model_url = config.get("gdrive_model_url")

    if not model_path.exists() and model_url:
        print(f"📥 Downloading model: {model_url}")
        gdown.download(model_url, str(model_path), quiet=False)

    llm = Llama(model_path=str(model_path), n_ctx=config.get("text-context", 16384 // 2), verbose=False)


    file_diffs = parse_diff_file(diff_path)
    if not file_diffs:
        print("⚠️ No relevant changes found in diff.")
        return

    review_dir = Path(config.get("review_dir"))
    review_dir.mkdir(exist_ok=True)

    for file, diff_chunk in file_diffs.items():
        prompt_prefix = config.get("prompt_prefix")
        prompt = f"{prompt_prefix}\nFile: `{file}`\nDiff:\n```diff\n{diff_chunk}\n```"
        print(f"🧠 Reviewing {file}\nPrompt:\n{prompt}")
        try:
            response = llm(prompt, max_tokens=config.get("max_tokens", 1024))
            suggestion = response["choices"][0]["text"].strip()

            output_file = review_dir / f"{Path(file).name}_{commit_id}.review.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"📝 Suggestions for {file}:\n{suggestion}\n")

        except Exception as e:
            print(f"❌ Error reviewing {file}: {e}")

    print(f"✅ Review completed. See {review_dir} folder for suggestions.\n{round(time.time()-start_time)} sec")
    print("REVIEW DONE")
