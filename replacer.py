import json
import signal
import sys
from pathlib import Path
from typing import Dict

from openai import OpenAI

# --- config ---
JSON_PATH = Path("eng_slo.json")
MODEL = "gpt-5-nano"
SAVE_EVERY = 10  # write file after this many updates
SLEEP_BETWEEN = 0.3  # seconds between API calls to be gentle

SYSTEM_PROMPT = """
I will give you an English word, and you will return its Slovenian translations. 
Please try to return at least 4 different translations. max better, but not more then 7
Return ONLY Slovenian translations, separated by commas. No extras.
"""
# (45000 - 22000) / 93000 = 24.7%
#  dispatching - meekness

client = OpenAI(
    api_key=""
)


def clean_translations(raw: str) -> str:
    parts = [p.strip() for p in raw.split(",")]
    # drop empties, dedupe, keep order, cap to 7
    seen, out = set(), []
    for p in parts:
        if not p:
            continue
        if p.lower() in seen:
            continue
        seen.add(p.lower())
        out.append(p)
        if len(out) >= 7:
            break
    return ", ".join(out)


def ask_gpt(word: str) -> str:
    r = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": word},
        ],
    )
    # OpenAI Python SDK v1: .output_text is the easiest way to get the text
    text = getattr(r, "output_text", None)
    if not text:
        # fall back: concatenate text parts just in case
        try:
            text = "".join(
                p.text
                for m in r.output
                if hasattr(m, "content")
                for p in m.content
                if getattr(p, "type", "") == "output_text"
            )
        except Exception:
            text = ""
    return clean_translations(text or "")


def save_file(data: Dict[str, str]) -> None:
    tmp = JSON_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(JSON_PATH)


def main():
    if not JSON_PATH.exists():
        print(f"File not found: {JSON_PATH}")
        sys.exit(1)

    with JSON_PATH.open("r", encoding="utf-8") as f:
        data: Dict[str, str] = json.load(f)

    updated_since_save = 0
    stop = False

    def handle_sigint(sig, frame):
        nonlocal stop
        stop = True
        print("\n⚠️  Interrupt received: finishing current word and saving…")

    signal.signal(signal.SIGINT, handle_sigint)

    for eng, val in data.items():
        if stop:
            break
        if eng.startswith("##"):
            continue
        if isinstance(val, str) and val.strip():
            continue  # skip non-empty
        if any(c.isspace() for c in eng):
            continue  # skip words with spaces. lets do spaces after
        # fetch translations
        try:
            sl = ask_gpt(eng)
            if sl:
                data[eng] = sl
                updated_since_save += 1
                print(f"✔ {eng} → {sl}")
            else:
                print(f"… {eng}: no result")
        except Exception as e:
            print(f"✖ {eng}: {e}")
        # periodic save
        if updated_since_save >= SAVE_EVERY:
            save_file(data)
            updated_since_save = 0
            print("💾 saved progress")
        # time.sleep(SLEEP_BETWEEN)

    # final save if needed
    if updated_since_save > 0:
        save_file(data)
        print("💾 final save")


if __name__ == "__main__":
    main()

"""
I will give you words in json format with empty values. 
write in values slovenian translations for keys. 
Try to find at least 5 translations for slovenian words and store them in value as one string, words are seperated by comma. 
More translations, better
Provide multiple valid Slovenian translations or synonyms, like in a bilingual dictionary. when writing json. also put comma after last value in a row like this:
{
"test": "trans1, trans2, trans3",
"test2": "trans1, trans2, trans3",
}

sounds ok?
"""
