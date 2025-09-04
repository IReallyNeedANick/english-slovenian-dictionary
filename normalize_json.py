import json

def normalize_json_keys(filepath: str):
    """
    Reads a JSON file, converts all its keys to lowercase,
    removes keys with empty values, sorts them,
    and writes the result back to the same file.

    Args:
        filepath (str): The path to the JSON file to process.
    """
    try:
        # Step 1: Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Step 2: Lowercase keys and remove empty values
        lowercase_data = {
            key.lower(): value
            for key, value in data.items()
            if value != ""  # skip empty values
        }

        # Step 3: Sort dictionary by key
        sorted_data = dict(sorted(lowercase_data.items()))

        # Step 4: Write back to the same file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)

        print(f"Success! '{filepath}' updated with lowercase keys, empty values removed, and sorted.")

    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{filepath}' contains invalid JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    json_file_path = 'eng_slo.json'
    normalize_json_keys(json_file_path)
