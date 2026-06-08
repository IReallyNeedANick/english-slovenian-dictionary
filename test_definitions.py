#!/usr/bin/env python3
import json
from pathlib import Path

# Učitaj JSON
json_path = Path("eng_slo.json")
with open(json_path, "r", encoding="utf-8") as f:
    dictionary = json.load(f)

# Ločimo metadata in besede
words = {k: v for k, v in dictionary.items() if not k.startswith("##")}

# Prikaži prvih 100 besed ki nimajo dobre razlage
word_list = list(words.items())
count = 0

print("Besede, ki potrebujejo razlago:\n")
for i, (word, translation) in enumerate(word_list[:500]):
    if not word.isdigit() and not word.startswith(".") and not word.startswith("("):
        parts = translation.split(",")
        # Besede s 3 ali manj deli verjetno trebajo razlago
        if len(parts) <= 3:
            print(f"{i+1}. {word}: {translation}")
            count += 1
            if count >= 30:
                break
