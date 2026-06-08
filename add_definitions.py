#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from anthropic import Anthropic

# Učitaj JSON
json_path = Path("eng_slo.json")
with open(json_path, "r", encoding="utf-8") as f:
    dictionary = json.load(f)

# Ločimo metadata in besede
metadata = {k: v for k, v in dictionary.items() if k.startswith("##")}
words = {k: v for k, v in dictionary.items() if not k.startswith("##")}

print(f"Skupno besed: {len(words)}")
print(f"Metapodatki: {len(metadata)}")

# Inicijaliziraj Anthropic klient
client = Anthropic()

def needs_explanation(word, translation):
    """Preveri, ali prevod potrebuje razlago"""
    # Če je prevod že dolg in ima vejice, ima verjetno že razlago
    parts = translation.split(",")
    if len(parts) >= 4:
        return False

    # Številke in kratice/tehnični izrazi pogosto ne trebajo razlage
    if word.isdigit() or word.startswith(".") or word.startswith("("):
        return False

    # Besede, ki so le prevodi brez pojašnjenja
    return True

def get_explanation(word, slovenian_translation):
    """Pridobi razlago od Claude za besedo"""
    prompt = f"""Slovenščina: Beseda "{word}" je prevedena kot "{slovenian_translation}".

Dodaj kratko, kvalitetno razlago v slovenščini (1-2 poved), ki pojasni, kaj beseda pomeni ali kako se uporablja.
Razlaga mora biti na slovenščini in konkretna.

Vrni samo razlago, brez dodatnih komentarjev.
Npr: "Se zavestno odpoveduje lastnim željam, udobju, užitkom ali pravicam."
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()

def process_batch(start_idx, batch_size=100):
    """Procesiraj eno skupino besed"""
    word_list = list(words.items())
    batch = word_list[start_idx:start_idx + batch_size]

    if not batch:
        return False

    print(f"\nProcesiram besede {start_idx + 1}-{min(start_idx + batch_size, len(word_list))}")

    updated = 0
    for word, translation in batch:
        if needs_explanation(word, translation):
            try:
                explanation = get_explanation(word, translation)
                new_translation = f"{translation}, {explanation}"
                words[word] = new_translation
                updated += 1
                print(f"  ✓ {word}")
            except Exception as e:
                print(f"  ✗ {word}: {e}")
        else:
            print(f"  - {word} (že ima razlago)")

    # Spravi rezultate
    save_dictionary()
    print(f"Spravljeno: {updated} besed v tej skupini")

    return True

def save_dictionary():
    """Spravi slovar nazaj v JSON"""
    combined = {**metadata, **words}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

def main():
    if len(sys.argv) > 1:
        start_idx = int(sys.argv[1])
    else:
        start_idx = 0

    if process_batch(start_idx, batch_size=100):
        next_idx = start_idx + 100
        print(f"\nNaslednja grupa: python add_definitions.py {next_idx}")
    else:
        print("Končano!")

if __name__ == "__main__":
    main()
