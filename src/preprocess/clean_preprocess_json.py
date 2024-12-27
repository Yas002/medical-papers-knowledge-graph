import json
import os
import re



def clean_text(text):
    if not isinstance(text, str):
        return text

    # Remove \\" 
    text = text.replace('"', '')

    # Remove substrings from 'xml_output' to the next backslash
    text = re.sub(r'xml_output.*?\\', '', text)

    # Remove newlines and tabs
    text = text.replace('\n', '').replace('\t', '')

    # Remove specific Unicode characters
    unwanted_unicode_chars = ['\u2022', '\u00a9', '\u03b1', '\u02dc']  # •, ©, α, ˜
    for char in unwanted_unicode_chars:
        text = text.replace(char, '')

    # Alternatively, to remove all non-ASCII characters, uncomment the following line:
    # text = re.sub(r'[^\x00-\x7F]+', '', text)

    return text




def clean_data(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {
        "paper_id": clean_text(data.get("paper_id")),
        "header": data.get("header"),
        "title": clean_text(data.get("title")),
        "authors": [
            {
                "first": author.get("first", "").strip(),
                "last": author.get("last", "").strip(),
                "email": author.get("email", "").strip(),
                "affiliation": author.get("affiliation", {})
            }
            for author in data.get("authors", [])
        ],
        "year": data.get("year"),
        "abstract": clean_text(data.get("abstract")),
        "pdf_parse_keywords": clean_text(data.get("pdf_parse", {}).get("keywords", [])),
        "body_text": [clean_text(item.get("text", "")) for item in data.get("pdf_parse", {}).get("body_text", [])],
        "back_matter": [clean_text(item.get("text", "")) for item in data.get("pdf_parse", {}).get("back_matter", [])],
        "bibref_titles": []
    }

    for key, val in data.get("pdf_parse", {}).get("bib_entries", {}).items():
        if key.startswith("BIBREF"):
            bib_title = clean_text(val.get("title", ""))
            if bib_title:
                result["bibref_titles"].append(bib_title)

    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(result, out_f, indent=2)

 # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the cleaned data to the output file
    try:
        with open(output_file, "w", encoding="utf-8") as out_f:
            json.dump(result, out_f, indent=2, ensure_ascii=False)
        print(f"Preprocessed data saved to {output_filepath}")
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    input_dir = "c:/Users/Yassine/Downloads/TanitAI_RAG/data/assignementdataset/"
    output_dir = "c:/Users/Yassine/Downloads/TanitAI_RAG/data/processed/"

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all JSON files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_filepath = os.path.join(input_dir, filename)
            output_filepath = os.path.join(output_dir, filename)
            clean_data(input_filepath, output_filepath)