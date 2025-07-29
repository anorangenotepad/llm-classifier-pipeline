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

# --- Build prompt (NO [INST] tags!) ---
prompt = (
    "You are a JSON-generating API. \n"
    "YOur task is to classify architectural image data. \n\n"
    "Respond only with valid, unescaped JSON.\n"
    "Do not use Markdown formatting or escape characters.\n\n"
    f"Given:\n"
    f"- Image Title: \"{image_title}\"\n"
    f"- Image JSON:\n{json.dumps(image_data, indent=2, ensure_ascii=False)}\n\n"
    f"- Bucket Name: \"{bucket_label}\"\n"
    f"- Bucket Features: {json.dumps(bucket_features, ensure_ascii=False)}\n\n"
    "TASK:\n"
    "Rate how well this image fits this bucket.\n"
    "Return only the following JSON structure:\n"
    "{\n"
    '  "image_title": "filename",\n'
    '  "semantic_confidence_score": 0.72,\n'
    '  "tier": "low / medium / high",\n'
    '  "reason": "Brief explanation"\n'
    "}\n"
    "The confidence score must be a number between 0.0 and 1.0.\n"
    "\Return only the following JSON object, nothing else — no Markdown, no backslashes, no formatting:\n"
)

# --- Write prompt ---
with open("semantic_prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

print("✅ Prompt written to semantic_prompt.txt")

