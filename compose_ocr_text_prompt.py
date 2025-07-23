import os

# === Settings ===
CHAR_LIMIT = 5000
DEFAULT_OUTPUT = "temp_ocr_text_prompt.txt"

# === Prompt user for a folder ===
input_dir = input("Enter path to OCR text folder: ").strip()

if not input_dir or not os.path.isdir(input_dir):
    print("❌ Error: Please input a valid directory path.\n")
    exit(1)

# === Collect .txt files ===
txt_files = sorted([
    os.path.join(input_dir, f)
    for f in os.listdir(input_dir)
    if f.lower().endswith(".txt")
])

if not txt_files:
    print("❌ No .txt files found in the directory.\n")
    exit(1)

# === Concatenate up to CHAR_LIMIT ===
combined_text = ""
for path in txt_files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if len(combined_text) + len(content) > CHAR_LIMIT:
        break
    combined_text += "\n\n" + content

if len(combined_text) >= CHAR_LIMIT:
    print(f"⚠️ Text capped at {CHAR_LIMIT} characters.")

# === Extract image_title from folder name ===
image_title = os.path.basename(os.path.normpath(input_dir))

# === Build prompt ===
prompt = "[INST] You are a historical document summarization assistant.\n\n"
prompt += f'image_title: "{image_title}"\n'
prompt += "Below is the OCR-extracted text from a scanned historical document:\n\n"
prompt += combined_text
prompt += "\n\nPlease return a JSON object containing:\n"
prompt += """{
  "image_title": "filename",
  "summary": "Short summary of the document",
  "scene": "Brief scene description",
  "objects": ["object1", "object2"],
  "architectural_style": "Architectural style if mentioned or implied",
  "notable_features": ["feature1", "feature2"],
  "estimated_time_period": "Rough time period (e.g. 1800s, mid-20th century)",
  "locations": ["region, city, or environment clues"],
  "reasoning": "Why you chose these values based on the text"
}
Only output valid, plain text JSON. Do not include anything outside the JSON block. Avoid escape sequences unless absolutely required for content.
[/INST]
"""

# === Save to file ===
with open(DEFAULT_OUTPUT, "w", encoding="utf-8") as f:
    f.write(prompt)

print(f"[✓] Prompt written to {DEFAULT_OUTPUT}")

