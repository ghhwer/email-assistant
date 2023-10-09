import json

def read_json_file(file_path):
    print(f'Processing JSON file. READ @ {file_path}')
    with open(file_path, 'r', encoding='utf8') as file:
        data = json.load(file)
    return data

def save_data_as_json(file_path, data):
    print(f'Processing JSON file. WRITE @ {file_path}')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)