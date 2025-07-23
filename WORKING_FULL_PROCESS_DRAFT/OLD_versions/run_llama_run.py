import subprocess
import json
import threading
import time
import re

def extract_last_json(text: str):
    """Extracts the last complete top-level JSON object from text using brace counting."""
    json_blocks = []
    brace_level = 0
    current_json = ""
    in_json = False

    for char in text:
        if char == '{':
            if not in_json:
                current_json = ''
                in_json = True
            brace_level += 1
        if in_json:
            current_json += char
        if char == '}':
            brace_level -= 1
            if brace_level == 0 and in_json:
                json_blocks.append(current_json)
                in_json = False

    # Try decoding from last to first
    for block in reversed(json_blocks):
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue

    return None


def kill_process_after_timeout(p, timeout=90):
    def target():
        time.sleep(timeout)
        if p.poll() is None:
            print("\n[!] Timeout reached. Killing process.")
            p.terminate()
    threading.Thread(target=target, daemon=True).start()

def run_llama_with_streaming(prompt_path: str, model_path: str, timeout: int = 90):
    print("[→] Launching streaming subprocess...")

    with open(prompt_path, "r") as f:
        prompt_content = f.read()

    command = [
        "/home/user/Tech/LLM/llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "--n-predict", "400",
        "--prompt", prompt_content
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    kill_process_after_timeout(process, timeout=timeout)

    full_output = []

    try:
        for line in process.stdout:
            print(line, end="")
            full_output.append(line)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        process.terminate()

    full_text = "".join(full_output)

    # Save raw output just in case
    with open("mistral_raw_output.txt", "w") as f:
        f.write(full_text)

    json_result = extract_last_json(full_text)
    if json_result:
        with open("mistral_result.json", "w") as f:
            json.dump(json_result, f, indent=2)
        print("\n[✓] Extracted JSON written to mistral_result.json")
        return {"status": "success", "file": "mistral_result.json"}

    print("\n[!] No valid JSON found.")
    return {"error": "No valid JSON found"}

# Entry point
if __name__ == "__main__":
    result = run_llama_with_streaming(
        prompt_path="temp_prompt.txt",
        model_path="/home/user/Tech/LLM/models/minstral/mistral-7b-instruct-v0.2.Q4_0.gguf",
        timeout=90  # your Goldilocks value
    )
    print("\n[RESULT]", result)

