import sys
import re
import json

#def extract_last_json_block(text: str) -> str:
#    """
#    Extracts the last complete top-level JSON object from a string.
#    """
#    brace_level = 0
#    current_block = []
#    json_blocks = []
#
#    for char in text:
#        if char == '{':
#            if brace_level == 0:
#                current_block = []
#            brace_level += 1
#        if brace_level > 0:
#            current_block.append(char)
#        if char == '}':
#            brace_level -= 1
#            if brace_level == 0:
#                json_blocks.append(''.join(current_block))
#
#    return json_blocks[-1] if json_blocks else None

def extract_last_json_block(text: str) -> str:
    """
    Extracts the last complete top-level JSON object from a string.
    Brace-level tracker works even with junk after the block.
    """
    brace_level = 0
    end = None
    start = None

    # Go backwards to find the last closing brace
    for i in range(len(text) - 1, -1, -1):
        if text[i] == '}':
            if end is None:
                end = i
            brace_level += 1
        elif text[i] == '{':
            brace_level -= 1
            if brace_level == 0:
                start = i
                break

    if start is not None and end is not None:
        return text[start:end+1]
    else:
        return None



def clean_text(text: str) -> str:
    """
    Removes hallucinated tokens and escapes.
    """
    # Remove [INST] tags and common garbage
    text = re.sub(r"\[/?INST\]", "", text)
    text = text.replace("\\_", "_")
    text = text.replace("\\\"", "\"")
    text = text.replace("> ", "")
    return text.strip()

def main():
    input_path = "mistral_raw_output.txt"
    output_path = sys.argv[1] if len(sys.argv) > 1 else "mistral_result.json"

    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_text(raw)
    json_block = extract_last_json_block(cleaned)

    if not json_block:
        print("❌ No valid JSON block found.")
        return

    try:
        parsed = json.loads(json_block)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        print(f"✅ Cleaned JSON written to {output_path}")
    except json.JSONDecodeError as e:
        print("❌ JSON decode error:")
        print(e)
        print("\nExtracted text:")
        print(json_block)

if __name__ == "__main__":
    main()

