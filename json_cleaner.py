import json
from pathlib import Path
import re

# Set these paths to match your system
input_dir = Path("/home/user/Tech/LLM/output")
output_dir = Path("/home/user/Tech/LLM/cleaned_output")
output_dir.mkdir(parents=True, exist_ok=True)

def extract_json_from_text(raw_text):
    try:
        # Isolate JSON block
        start = raw_text.index('{')
        json_text = raw_text[start:]

        # Fix common invalid escape: \_
        json_text = re.sub(r'\\_', '_', json_text)

        return json.loads(json_text)
    except Exception as e:
        print(f"[!] Failed to extract JSON: {e}")
        return None

def clean_all_json_files():
    for file in input_dir.glob("*.json"):
        print(f"[→] Cleaning {file.name}")
        text = file.read_text()
        data = extract_json_from_text(text)
        if data:
            out_path = output_dir / file.name
            out_path.write_text(json.dumps(data, indent=2))
            print(f"[✓] Saved cleaned JSON to {out_path.name}")
        else:
            print(f"[!] Skipped {file.name} due to parse error")

if __name__ == "__main__":
    clean_all_json_files()

