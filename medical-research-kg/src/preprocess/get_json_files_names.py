import os

def get_json_file_names(directory_path):
    json_files = [file for file in os.listdir(directory_path) if file.endswith('.json')]
    return json_files

# Example usage:
directory_path = "C:/Users/Yassine/Downloads/TanitAI_RAG/medical-research-kg/data/assignementdataset/assignementdataset"
json_file_names = get_json_file_names(directory_path)
print(json_file_names)
