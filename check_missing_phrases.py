import json

# input file paths
ENG_SLO_FILE = "eng_slo.json"
OUTPUT_FILE = "missing_phrases.json"

def main():

    with open(ENG_SLO_FILE, "r", encoding="utf-8") as f:
        eng_slo = json.load(f)

    # Normalize keys from eng_slo to lowercase
    empty_keys = [k for k, v in eng_slo.items() if v == ""]


    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(empty_keys, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(empty_keys)} missing keys saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
