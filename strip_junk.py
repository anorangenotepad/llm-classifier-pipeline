import re
from pathlib import Path
import json

def extract_valid_json(path):
    text = Path(path).read_text()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print("JSON error:", e)
    else:
        print("No JSON found.")
    return None

result = extract_valid_json("mistral_raw_output.txt")
print(result)

