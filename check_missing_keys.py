import json

BIGGER_FILE = "output_wordnet.json"
SMALLER_FILE = "eng_slo.json"
OUTPUT_FILE = "missing_keys_wordnet.json"
DROP_WORDS = True

def main():
    with open(BIGGER_FILE, "r", encoding="utf-8") as f:
        de_eng = json.load(f)
    with open(SMALLER_FILE, "r", encoding="utf-8") as f:
        eng_slo = json.load(f)

    # normalize keys to lowercase for comparison
    eng_slo_keys = {k.lower() for k in eng_slo.keys()}
    de_eng = {k.lower() for k in de_eng.keys()}

    missing_keys = {k: "" for k in de_eng if k.lower() not in eng_slo_keys}

    if DROP_WORDS:
        missing_keys = {key: value for key, value in missing_keys.items() if ' ' not in key}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(missing_keys, f, ensure_ascii=False, indent=2)

    print(f"Missing keys found: {len(missing_keys)}")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
