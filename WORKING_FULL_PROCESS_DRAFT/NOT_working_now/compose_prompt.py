import json
import os

# Load files
#input_path = "./cleaned_output/structured_service-pnp-habshaer-mi-mi0600-mi0687-photos-196664pr.json"
user_input = input(f"Enter path to structured image JSON: ").strip()
if not user_input:
    print("❌ Error: Please input a file path.\n")
    exit(1)  # Exit the script
#input_path = user_input

import json
import os

# Load existing processed image titles by plain text search
processed_titles = set()
last_block_path = "last_block.json"

# Extract image title from input_path (remove path and .json extension)
input_filename = os.path.basename(input_path)
image_title = os.path.splitext(input_filename)[0].replace("structured_", "")

if os.path.exists(last_block_path):
    with open(last_block_path, "r", encoding="utf-8") as f:
        contents = f.read()
        if f'"image_title": "{image_title}"' in contents:
            print(f"⚠️  Image '{image_title}' has already been processed. Skipping.")
            exit(0)

# Extract image title from input_path (remove path and .json extension)
input_filename = os.path.basename(input_path)
image_title = os.path.splitext(input_filename)[0].replace("structured_", "")



# Check if already processed
if image_title in processed_titles:
    print(f"⚠️  Image '{image_title}' has already been processed. Skipping.")
    exit(0)

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

