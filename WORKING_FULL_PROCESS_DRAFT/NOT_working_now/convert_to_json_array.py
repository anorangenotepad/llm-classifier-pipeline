import json

def convert_to_array(input_file='last_block.json', output_file='last_block_array.json'):
    with open(input_file, 'r') as f:
        lines = [json.loads(line) for line in f if line.strip()]

    with open(output_file, 'w') as f:
        json.dump(lines, f, indent=2)

    print(f"✅ Converted {len(lines)} JSON objects into array at {output_file}")

if __name__ == '__main__':
    convert_to_array()

