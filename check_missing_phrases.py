import json

# input file paths
DE_ENG_FILE = "de_eng-deu.json"
ENG_SLO_FILE = "eng_slo.json"
OUTPUT_FILE = "missing_phrases.json"

def main():
    with open(DE_ENG_FILE, "r", encoding="utf-8") as f:
        de_eng = json.load(f)
    with open(ENG_SLO_FILE, "r", encoding="utf-8") as f:
        eng_slo = json.load(f)

    # keys in de_eng but not in eng_slo
    missing_keys = {k: "" for k in de_eng.keys() if k not in eng_slo}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(missing_keys, f, ensure_ascii=False, indent=2)

    print(f"Done. Missing keys saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
