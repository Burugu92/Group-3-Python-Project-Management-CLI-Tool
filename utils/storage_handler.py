import os
import json

def save_to_file(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    data_to_save = []
    for item in data:
        if hasattr(item, 'to_dict'):
            data_to_save.append(item.to_dict())
        elif isinstance(item, dict):
            data_to_save.append(item)
        elif hasattr(item, '__dict__'):
            data_to_save.append(item.__dict__)
        else:
            data_to_save.append(str(item))
    try:
        with open(filename, 'w') as file:
            json.dump(data_to_save, file, indent=4)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        
    
        
def load_from_file(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []