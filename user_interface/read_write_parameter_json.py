import json
import os

# Get the directory of json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'parameters.json')

def read_parameter_json():
    """
    Read parameters.json and return its content as python dictionary.
    Returns None if an error occurs.
    """
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {JSON_FILE} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {JSON_FILE} contains invalid JSON.")
        return None
    except PermissionError:
        print(f"Error: Permission denied when reading {JSON_FILE}.")
        return None
    except Exception as e:
        print(f"Unexpected error reading {JSON_FILE}: {str(e)}")
        return None

def write_parameter_json(dict_data):
    """
    Writes dictionary data to parameters.json.
    Returns True if successful, False otherwise.
    """
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(dict_data, file, indent=4)
        return True
    except PermissionError:
        print(f"Error: Permission denied when writing to {JSON_FILE}.")
        return False
    except Exception as e:
        print(f"Unexpected error writing to {JSON_FILE}: {str(e)}")
        return False