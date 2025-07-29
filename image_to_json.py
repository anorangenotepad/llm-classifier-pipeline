import subprocess
import os
from pathlib import Path

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent

# CONFIG
llava_bin = BASE_DIR / "llama.cpp/build/bin/llama-mtmd-cli"
model_path = BASE_DIR / "models/llava/llava-v1.5-13b-Q4_0.gguf"
mmproj_path = "models/llava-mmproj/mmproj-model-f16.gguf"
image_dir = BASE_DIR / "images"
output_dir = BASE_DIR / "output"
chat_template = "vicuna"
prompt = (
    "Analyze the following image and return only the following JSON structure:\n"
    "{\n"
    '  "scene": "string",\n'
    '  "objects": ["string"],\n'
    '  "architectural_style": "string",\n'
    '  "notable_features": ["string"],\n'
    '  "estimated_time_period": "string",\n'
    '  "locations": ["string"],\n'
    '  "reasoning": "string",\n'
    '  "description": "string"\n'
    "}\n"
    "Only output valid JSON. Do not include explanations outside the structure."
)


# Make sure output dir exists
output_dir.mkdir(parents=True, exist_ok=True)

# Loop through images
for image_path in image_dir.glob("*.[Jj][Pp][Gg]"):
    output_path = output_dir / f"structured_{image_path.stem}.json"
    if output_path.exists():
        print(f"[✓] Skipping {image_path.name} (already exists)")
        continue

    print(f"[→] Processing {image_path.name}")
    cmd = [
        llava_bin,
        "-m", model_path,
        "--mmproj", mmproj_path,
        "--image", str(image_path),
        "--prompt", prompt,
        "--chat-template", chat_template
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            output_path.write_text(result.stdout.strip())
            print(f"[✓] Saved to {output_path.name}")
        else:
            print(f"[!] Error on {image_path.name}:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"[!] Timeout on {image_path.name}")

