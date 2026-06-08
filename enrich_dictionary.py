#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from anthropic import Anthropic

# Učitaj JSON
json_path = Path("eng_slo.json")
with open(json_path, "r", encoding="utf-8") as f:
    dictionary = json.load(f)

# Ločimo metapodatke in besede
metadata = {k: v for k, v in dictionary.items() if k.startswith("##")}
words = {k: v for k, v in dictionary.items() if not k.startswith("##")}

print(f"Skupno besed: {len(words)}")

# Inicijaliziraj Anthropic klient
client = Anthropic()

def should_skip_word(word):
    """Preskoči besede, ki ne trebajo razlage"""
    # Preskoči številke, datume, tehnične izraze
    if word.isdigit():
        return True
    if word.startswith("."):
        return True
    if word.startswith("("):
        return True
    # Besede s pomišljaji (večbesedni izrazi) pogosto že imajo razlago
    if word.count("-") > 1:
        return True
    return False

def has_good_explanation(translation):
    """Preveri, ali prevod že ima dobro razlago"""
    # Če je prevod že dolg (več kot 100 znakov), verjetno ima razlago
    if len(translation) > 100:
        return True
    # Besede, ki imajo že pojašnjilo (npr. s podčrtajem v smislu "...")
    if " - " in translation:
        return True
    return False

def add_explanation(word, slovenian_translation):
    """Dodaj razlago s pomočjo Claude-a"""
    prompt = f"""Ti si strokovnjak za angleško-slovenski slovar. Beseda "{word}" je prevedena kot: "{slovenian_translation}".

Dodaj kratko, precizno razlago v slovenščini (1-2 povedi), ki pojasni, kaj beseda pomeni ali kako se uporablja.
Razlaga mora biti konkretna in na slovenščini.

Primer:
- Za "abnegator" bi bila razlaga: "Oseba, ki se zavestno odpoveduje lastnim željam in udobju."
- Za "abound" bi bila razlaga: "Obstajati ali biti prisotna v veliki količini."

Vrni samo razlago, brez navodil ali dodatnih besed.
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()

def process_batch(start_idx, batch_size=10):
    """Procesiraj eno skupino besed"""
    word_list = list(words.items())
    batch = word_list[start_idx:start_idx + batch_size]

    if not batch:
        print("Konec!")
        return False

    print(f"\nProcesiram besede {start_idx + 1}-{min(start_idx + batch_size, len(word_list))}")
    print("=" * 60)

    updated = 0
    skipped = 0

    for word, translation in batch:
        # Preskoči besede, ki ne trebajo razlage
        if should_skip_word(word):
            skipped += 1
            continue

        # Preskoči besede, ki že imajo dobro razlago
        if has_good_explanation(translation):
            print(f"✓ {word}: že ima razlago")
            skipped += 1
            continue

        try:
            explanation = add_explanation(word, translation)
            new_translation = f"{translation}, {explanation}"
            words[word] = new_translation
            updated += 1
            print(f"➕ {word}")
            print(f"   Prevod: {translation}")
            print(f"   Razlaga: {explanation}")
        except Exception as e:
            print(f"✗ {word}: Napaka - {e}")

    # Spravi rezultate
    save_dictionary()
    print("=" * 60)
    print(f"Rezultati: {updated} besed posodobljenih, {skipped} preskokov")

    return True

def save_dictionary():
    """Spravi slovar nazaj v JSON"""
    combined = {**metadata, **words}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print("Datoteka shranjena!")

def main():
    if len(sys.argv) > 1:
        start_idx = int(sys.argv[1])
    else:
        start_idx = 0

    if process_batch(start_idx, batch_size=10):
        next_idx = start_idx + 10
        print(f"\nNaslednja grupa: python3 enrich_dictionary.py {next_idx}")
    else:
        print("Konec!")

if __name__ == "__main__":
    main()
