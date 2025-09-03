# build_stardict.py
import json, struct, os

INPUT_JSON = "eng_slo.json"
OUTPUT_BASENAME = "stardict_eng_slo"  # produces .ifo/.idx/.dict

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # sort for consistent index
    items = sorted(data.items(), key=lambda kv: kv[0])

    dict_path = OUTPUT_BASENAME + ".dict"
    idx_path  = OUTPUT_BASENAME + ".idx"
    ifo_path  = OUTPUT_BASENAME + ".ifo"

    offset = 0
    idx_bytes = bytearray()

    with open(dict_path, "wb") as df:
        for head, defin in items:
            head_b = head.encode("utf-8")
            defi_b = (defin or "").encode("utf-8")
            # write definition to .dict
            df.write(defi_b)
            size = len(defi_b)
            # .idx: headword + NUL + offset(4B BE) + size(4B BE)
            idx_bytes += head_b + b"\x00" + struct.pack(">II", offset, size)
            offset += size

    with open(idx_path, "wb") as ix:
        ix.write(idx_bytes)

    # .ifo header
    ifo = [
        "StarDict's dict ifo file",
        "version=3.0.0",
        f"bookname={OUTPUT_BASENAME}",
        f"wordcount={len(items)}",
        f"idxfilesize={len(idx_bytes)}",
        "sametypesequence=m",  # plain text
        "",
    ]
    with open(ifo_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ifo))

    print("Done:",
          os.path.abspath(ifo_path),
          os.path.abspath(idx_path),
          os.path.abspath(dict_path), sep="\n")

if __name__ == "__main__":
    main()
