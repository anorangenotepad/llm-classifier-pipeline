#!/bin/bash

FILE="mistral_raw_output.txt"

# Clean up from prior runs
> valid_blocks.tmp
> last_block.json

awk '
BEGIN {
  in_json = 0
  in_response = 0
  json = ""
  depth = 0
}
{
  if ($0 ~ /\[\/INST\]/) {
    in_response = 1
  }
  if (in_response) {
    for (i = 1; i <= length($0); i++) {
      ch = substr($0, i, 1)
      if (ch == "{") {
        if (depth == 0) json = ""
        in_json = 1
        depth++
      }
      if (in_json) json = json ch
      if (ch == "}") {
        depth--
        if (depth == 0 && in_json == 1) {
          print json > "valid_blocks.tmp"
          in_json = 0
        }
      }
    }
  }
}
' "$FILE"

# Pull last complete block and validate with jq
if [ -s valid_blocks.tmp ]; then
  tail -n 1 valid_blocks.tmp >> last_block.json
  if jq empty last_block.json 2>/dev/null; then
    echo "✅ Last valid JSON block:"
    jq . last_block.json
  else
    echo "❌ Found something after [INST], but it’s not valid JSON:"
    cat last_block.json
  fi
else
  echo "❌ No JSON found after final [INST]."
fi

