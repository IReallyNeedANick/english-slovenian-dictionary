import sys
from pathlib import Path
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Any, Dict

from google import genai
from google.genai import types
from pydantic import BaseModel

# --- config ---
JSON_PATH = Path("missing_phrases.json")
MODEL = "gpt-5-nano"
SAVE_EVERY = 10  # write file after this many updates
SLEEP_BETWEEN = 0.3  # seconds between API calls to be gentle

class TranslationObject(BaseModel):
    w: str
    t: str

SYSTEM_PROMPT = """

You will receive an array of English words or phrases.
Return a JSON array of objects where:
 - w = the English word or phrase
 - t = a comma-separated string of Slovenian translations (5–8 different ones if possible, covering different meanings and contexts)

Rules:
 - Output valid JSON only.
 - Each t value must contain only Slovenian words/translations/descriptions, separated by commas.
 - If a word has no native Slovenian equivalent, include the loanword and short explanation in Slovenian (inside the t string).
 - Please try to return at least 5 different translations for every english word. As much as possible different translations depending on different context.
 - Max better, but not more then 8 different translations.
 
Example input:
["room", "broom"]

Example output:
[
  {"w": "room", "t": "soba, prostor, priložnost, možnost, namestitev"},
  {"w": "broom", "t": "metla, brezovka, metlica, čistilni pripomoček, čarovniška metla"}
]

"""

client = genai.Client(
    api_key =""
)


def process_batches(batches: List[Any], data: Dict[str, str], concurrency: int = 10) -> Dict[str, str]:
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        # process in chunks of `concurrency`
        futures = [ex.submit(ask_gemini, json.dumps(b, indent=2)) for b in batches]

        for fut in as_completed(futures):
            try:
                gemini_return = fut.result()
            except Exception as e:
                print("ask_gemini failed:", e)
                continue

            # update shared dict under lock
            with lock:
                if gemini_return is not None:
                    for translation in gemini_return:
                        # support both dicts and objects with attributes
                        if isinstance(translation, dict):
                            w = translation.get("w")
                            t = translation.get("t")
                        else:
                            w = getattr(translation, "w", None)
                            t = getattr(translation, "t", None)

                        if w is not None:
                            data[w] = t
                else:
                    print('return was none')

        save_file(data)

    return data

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


def ask_gemini(word: str) -> list[TranslationObject]:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=
        types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type= "application/json",
            response_schema= list[TranslationObject]
        ),
        contents=word,
    )

    translations: list[TranslationObject] = response.parsed

    return translations


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

    batches = []
    batch = []
    counter = 0
    for eng, val in data.items():
        if eng.startswith("##"):
            continue
        if len(eng.strip()) == 0:
            continue
        if isinstance(val, str) and val.strip():
            continue  # skip non-empty

        # fetch translations
        if counter >= 50:
            batches.append(batch)
            counter = 0
            batch = []

        batch.append(eng)
        counter = counter + 1

    if counter > 0:
        batches.append(batch)

    print(f"Processing {len(batches)} batches")
    chunk_size = 10
    for i in range(0, len(batches), chunk_size):
        chunk = batches[i : i + chunk_size]
        process_batches(chunk, data)
        print(f"💾 saved progress {i}/ {len(batches)}")

    # for batch in batches:
    #     gemini_return= ask_gemini(json.dumps(batch, indent=2))
    #
    #     for translation in gemini_return:
    #         data[translation.w] = translation.t
    #
    #     save_file(data)
    #     print("💾 saved progress")

if __name__ == "__main__":
    main()

