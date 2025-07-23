import json
import os

# --- Paths ---
BUCKET_FILE = "habs_buckets_mvp.json"

# --- Input ---
input_path = input("Enter path to structured image JSON: ").strip()
best_match_label = input("Enter best match bucket label: ").strip()

if not input_path or not best_match_label:
    print("❌ Error: Please provide both inputs.\n")
    exit(1)

if not os.path.exists(input_path):
    print(f"❌ File not found: {input_path}")
    exit(1)

# --- Load files ---
with open(input_path, "r", encoding="utf-8") as f:
    image_data = json.load(f)

with open(BUCKET_FILE, "r", encoding="utf-8") as f:
    all_buckets = json.load(f)

# --- Extract bucket ---
bucket_entry = next((b for b in all_buckets if b["label"] == best_match_label), None)
if not bucket_entry:
    print(f"❌ Bucket label not found: {best_match_label}")
    exit(1)

bucket_features = bucket_entry.get("notable_features", [])
bucket_label = bucket_entry["label"]

# --- Extract image title ---
image_title = os.path.basename(input_path).replace("structured_", "").replace(".json", "")

# --- Build prompt ---
prompt = "[INST] You are a semantic classifier of historical architectural data.\n\n"
prompt += f"Given:\n- Image Title: \"{image_title}\"\n"
prompt += f"- Image JSON:\n{json.dumps(image_data, indent=2, ensure_ascii=False)}\n\n"
prompt += f"- Bucket Name: \"{bucket_label}\"\n"
prompt += f"- Bucket Features: {json.dumps(bucket_features, ensure_ascii=False)}\n\n"

prompt += (
    "TASK:\n"
    "Rate how well this image fits this bucket. Return a JSON object like this:\n"
    "{\n"
    "  \"image_title\": \"filename\",\n"
    "  \"semantic_confidence_score\": 0.72,\n"
    "  \"tier\": \"low / medium / high\",\n"
    "  \"reason\": \"Brief explanation\"\n"
    "}\n"
    "Confidence score must be between 0.0 and 1.0.\n"
    "Do not include any other text.\n"
    "[/INST]"
)

# --- Write prompt ---
with open("semantic_prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

print("✅ Prompt written to semantic_prompt.txt")
