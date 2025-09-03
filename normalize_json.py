import json

def normalize_json_keys(filepath: str):
    """
    Reads a JSON file, converts all its keys to lowercase, sorts them,
    and writes the result back to the same file.

    Args:
        filepath (str): The path to the JSON file to process.
    """
    try:
        # Step 1: Read the JSON file with UTF-8 encoding
        # This is important for handling special characters in Slovenian.
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Step 2: Make all keys lowercase
        # A dictionary comprehension is an efficient way to do this.
        lowercase_data = {key.lower(): value for key, value in data.items()}

        # Step 3: Sort the dictionary alphabetically by key
        sorted_data = dict(sorted(lowercase_data.items()))

        # Step 4: Write the processed data back to the same file
        # 'indent=4' makes the file readable (pretty-prints).
        # 'ensure_ascii=False' ensures Slovenian characters are saved correctly.
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)

        print(f"Success! The file '{filepath}' has been updated with lowercase and sorted keys.")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found. Please make sure it's in the correct directory.")
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' contains invalid JSON. Please check the file format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Specify the name of your JSON file here
    json_file_path = 'eng_slo.json'
    normalize_json_keys(json_file_path)
