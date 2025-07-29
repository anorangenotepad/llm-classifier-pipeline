import json
import os

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    mistral_path = "mistral_result.json"
    if not os.path.exists(mistral_path):
        print(f"❌ File '{mistral_path}' not found. Run clean_mistral_output.py first.")
        return

    try:
        mistral_data = load_json_file(mistral_path)
    except json.JSONDecodeError as e:
        print(f"❌ Error reading {mistral_path}: {e}")
        return

    target_path = input("📂 Enter the path to the JSON file you want to append to: ").strip()

    if not os.path.exists(target_path):
        print(f"⚠️ File '{target_path}' not found. Creating new JSON array...")
        output_data = [mistral_data]
    else:
        try:
            if os.path.getsize(target_path) == 0:
                print("⚠️ Target file is empty. Starting new JSON array...")
                output_data = [mistral_data]
            else:
                existing_data = load_json_file(target_path)
                if isinstance(existing_data, list):
                    output_data = existing_data + [mistral_data]
                elif isinstance(existing_data, dict):
                    output_data = {**existing_data, **mistral_data}
                else:
                    print("❌ Unsupported JSON structure (not list or dict).")
                    return
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Error reading {target_path}: {e}")
            return

    write_json_file(target_path, output_data)
    print(f"✅ Appended data to {target_path}")

if __name__ == "__main__":
    main()

