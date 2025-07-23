import json
import os

# Load files
input_path = "./cleaned_output/structured_0412001564-l.json"
with open(input_path, "r", encoding="utf-8") as f:
    llava_data = json.load(f)

with open("habs_buckets_mvp.json", "r", encoding="utf-8") as f:
    buckets = json.load(f)

# Get image title from filename
image_title = os.path.basename(input_path).replace("structured_", "").replace(".json", "")

# Build prompt
prompt = "[INST] You are a historical records analyst.\n\n"
prompt += f'image_title: "{image_title}"\n'
prompt += "Below is the description of an item:\n"

# Ordered fields from llava_result.json
for key in ["scene", "objects", "architectural_style", "notable_features", "estimated_time_period", "locations", "reasoning"]:
    if key in llava_data:
        prompt += f"{key}: {json.dumps(llava_data[key], ensure_ascii=False)}\n"

prompt += "\nHere is a list of classification buckets:\n\n"

# Add each bucket from JSON file
for bucket in buckets:
    prompt += f"- {bucket['label']}: {bucket['notable_features']}\n"

# Add instructions
prompt += (
    "Based on the item's description, choose the most appropriate classification bucket.\n"
    "Return only the following JSON structure:\n"
    "{\n"
    '  "image_title": "filename",\n'
    '  "best_match": "label",\n'
    '  "confidence_score": "high / medium / low",\n'
    '  "reasoning": "string"\n'
    "}\n"
    "Only output valid JSON. Do not include explanations outside the structure.\n"
    "[/INST]"
)

# Write output
with open("temp_prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

print("[✓] Prompt written to temp_prompt.txt")

