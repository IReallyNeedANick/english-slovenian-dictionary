#!/usr/bin/env python3
import json
import sys

def load_dictionary():
    with open("eng_slo.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_dictionary(data):
    with open("eng_slo.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_words_needing_explanation(start_idx=0, batch_size=100):
    """Najdi besede, ki trebajo razlago"""
    dictionary = load_dictionary()

    words = {k: v for k, v in dictionary.items() if not k.startswith("##")}
    word_list = list(words.items())

    candidates = []

    for word, translation in word_list[start_idx:start_idx + batch_size * 10]:
        # Preskoči besede, ki ne trebajo razlage
        if word.isdigit() or word.startswith("."):
            continue

        # Preskoči besede, ki začnejo s številko
        if word[0].isdigit():
            continue

        # Preskoči ordinalne brojeve in prefiksne izraze
        if word.endswith("th") or word.endswith("st") or word.endswith("nd") or word.endswith("rd"):
            continue

        # Preskoči zagrade izraze
        if word.startswith("(") or word.endswith(")"):
            continue

        # Preskoči besede s dolgim prevodom (verjetno že imajo razlago)
        if len(translation) > 100:
            continue

        # Besede s kratkim prevodom in vejicami, ampak ni preskupkov
        if "," in translation and len(translation.split(",")) <= 4:
            # Preskoči besede, ki so samo prevodi različnih oblik (rod, število...)
            parts = [p.strip() for p in translation.split(",")]
            if len(parts) == len(set(p.split()[0] for p in parts if p)):
                candidates.append((word, translation))

    return candidates

def update_words(updates):
    """Posodobi slovar z novimi razlagami"""
    dictionary = load_dictionary()

    for word, new_translation in updates.items():
        dictionary[word] = new_translation

    save_dictionary(dictionary)
    print(f"✓ Posodobljenih {len(updates)} besed")

def show_batch(start_idx=0, batch_size=10):
    """Prikaži skupino besed, ki trebajo razlago"""
    candidates = find_words_needing_explanation(start_idx, batch_size * 5)

    print(f"\nBesede za obogatitev ({start_idx + 1}-{start_idx + len(candidates)}):")
    print("=" * 70)

    for i, (word, translation) in enumerate(candidates[:batch_size]):
        print(f"{i+1}. {word}: {translation}")

    print("=" * 70)
    return candidates[:batch_size]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uporaba:")
        print("  python3 batch_enrich.py show [indeks]  - Prikaži besede")
        print("  python3 batch_enrich.py update word1 'prevod1 + razlaga' word2 'prevod2 + razlaga'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "show":
        start_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        show_batch(start_idx)
    elif command == "update":
        updates = {}
        for i in range(2, len(sys.argv), 2):
            if i + 1 < len(sys.argv):
                word = sys.argv[i]
                translation = sys.argv[i + 1]
                updates[word] = translation
        update_words(updates)
