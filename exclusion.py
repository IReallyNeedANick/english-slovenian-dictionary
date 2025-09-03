import json
from pathlib import Path

# --- paths ---
all_words_path = Path("all_words.json")
eng_slo_path = Path("eng_slo.json")
missing_path = Path("missing_words.json")

# --- load files ---
with all_words_path.open("r", encoding="utf-8") as f:
    all_words = json.load(f)   # array of words

with eng_slo_path.open("r", encoding="utf-8") as f:
    eng_slo = json.load(f)     # dict of key->value

# --- filter out existing keys ---
missing = {word: "" for word in all_words if word not in eng_slo}

# --- save result ---
with missing_path.open("w", encoding="utf-8") as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)

print(f"Saved {len(missing)} missing words to {missing_path}")
