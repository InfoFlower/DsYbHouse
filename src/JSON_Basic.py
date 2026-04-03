import json

def save_json(data, filename):
    try :
        with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON to {filename}: {e}")

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)