import json
import os
from rapidfuzz import fuzz

# --- Config ---
CLEANED_DIR = "cleaned_output"
BUCKET_FILE = "habs_buckets_mvp.json"
LAST_BLOCK_FILE = "last_block.json"
OUTPUT_FILE = "scored_matches.jsonl"


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)



def score_confidence(item, matched_bucket_name, matched_bucket_features):
    score = 0.0

    # Adjusted weights
    WEIGHTS = {
        "objects": 0.3,
        "style": 0.3,
        "features": 0.2,
        "location": 0.1,
        "token_match": 0.1
    }

    # 1. Objects
    if item.get("objects"):
        object_text = " ".join(item["objects"]).lower()
        score += WEIGHTS["objects"] * (fuzz.token_set_ratio(object_text, matched_bucket_name.lower()) / 100.0)

    # 2. Architectural Style
    if item.get("architectural_style"):
        score += WEIGHTS["style"] * (fuzz.token_set_ratio(item["architectural_style"].lower(), matched_bucket_name.lower()) / 100.0)

    # 3. Notable Features
    if item.get("notable_features"):
        match_count = 0
        for nf in item["notable_features"]:
            for bf in matched_bucket_features:
                if fuzz.token_set_ratio(nf.lower(), bf.lower()) > 50:
                    match_count += 1
                    break
        feature_score = match_count / len(matched_bucket_features)
        score += WEIGHTS["features"] * min(feature_score, 1.0)

    # 4. Location bonus
    if "menomonie" in " ".join(item.get("locations", [])).lower():
        score += WEIGHTS["location"]

    # 5. Bucket features mentioned in input
    all_text_fields = " ".join([
        " ".join(item.get("objects", [])),
        item.get("architectural_style", ""),
        " ".join(item.get("notable_features", []))
    ]).lower()
    token_match = sum(1 for bf in matched_bucket_features if bf.lower() in all_text_fields)
    token_score = token_match / len(matched_bucket_features)
    score += WEIGHTS["token_match"] * min(token_score, 1.0)


    # 6. NEW: Check for bucket feature terms anywhere in full cleaned JSON text
    json_blob = json.dumps(item).lower()
    bucket_token_hits = sum(1 for bf in matched_bucket_features if bf.lower() in json_blob)
    bucket_blob_score = bucket_token_hits / len(matched_bucket_features)
    score += 0.1 * bucket_blob_score  # add new weight for this



    # Normalize and compute tier
    normalized_score = round(score / 1.1, 3)

    if normalized_score >= 0.75:
        tier = "high"
    elif normalized_score >= 0.45:
        tier = "medium"
    else:
        tier = "low"

    print(f"""
      [{item.get('objects', ['?'])[0]}]
      Match: {matched_bucket_name}
      Object Score: {fuzz.token_set_ratio(object_text, matched_bucket_name.lower()) / 100.0:.2f}
      Style Score:  {fuzz.token_set_ratio(item.get("architectural_style", "").lower(), matched_bucket_name.lower()) / 100.0:.2f}
      Features Score: {feature_score:.2f}
      Location Bonus: {WEIGHTS['location'] if "menomonie" in " ".join(item.get("locations", [])).lower() else 0:.2f}
      Token Mention Score: {token_score:.2f}
      JSON Blob Score: {bucket_blob_score:.2f}
      Final Normalized Score: {normalized_score:.3f}
      Confidence Tier: {tier.upper()}
    """)

    return normalized_score, tier



    #normalized_score = round(score / 1.1, 3)
    #return normalized_score

def process_all():
    # Load bucket definitions
    buckets = load_json(BUCKET_FILE)

    #raw_buckets = load_json(BUCKET_FILE)

    # Convert if needed
    #if isinstance(raw_buckets, list):
        #buckets = {entry["label"]: entry["features"] for entry in raw_buckets}
    #else:
        #buckets = raw_buckets

    results = []

    with open(LAST_BLOCK_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        try:
            entry = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ Skipping malformed JSON line:\n{line}")
            continue

        image_title = entry.get("image_title")
        best_match = entry.get("best_match")

        if not image_title or not best_match:
            print(f"⚠️ Missing fields in entry: {entry}")
            continue

        #cleaned_path = os.path.join(CLEANED_DIR, f"{image_title}.json")
        #if not os.path.exists(cleaned_path):
            #print(f"❌ Cleaned JSON not found for: {image_title}")
            #continue

        # Try both "image_title.json" and "structured_image_title.json"
        base_filename = f"{image_title}.json"
        structured_filename = f"structured_{image_title}.json"

        cleaned_path = None
        if os.path.exists(os.path.join(CLEANED_DIR, base_filename)):
            cleaned_path = os.path.join(CLEANED_DIR, base_filename)
        elif os.path.exists(os.path.join(CLEANED_DIR, structured_filename)):
            cleaned_path = os.path.join(CLEANED_DIR, structured_filename)
        else:
            print(f"❌ Cleaned JSON not found for: {image_title}")
            continue

        try:
            item_data = load_json(cleaned_path)
        except Exception as e:
            print(f"❌ Failed to load {cleaned_path}: {e}")
            continue


        #bucket_features = buckets.get(best_match)
        #if not bucket_features:
            #print(f"⚠️ No bucket found for: {best_match}")
            #continue



        # Find the bucket entry with matching label
        bucket_entry = next((b for b in buckets if b["label"] == best_match), None)

        if not bucket_entry:
            print(f"⚠️ No bucket found for: {best_match}")
            continue

        bucket_features = bucket_entry.get("notable_features", [])


        #real_score = score_confidence(item_data, best_match, bucket_features)

        real_score, tier = score_confidence(item_data, best_match, bucket_features)
        
        output_entry = {
            "image_title": image_title,
            "best_match": best_match,
            "real_confidence_score": real_score,
            "confidence_tier": tier
        }

        results.append(output_entry)

    # Write newline-delimited JSON
    with open(OUTPUT_FILE, "w") as f:
        for entry in results:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Scored {len(results)} entries → {OUTPUT_FILE}")


if __name__ == "__main__":
    process_all()
