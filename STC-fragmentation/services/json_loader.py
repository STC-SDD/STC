import json
from json import JSONDecodeError

def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        if default is not None:
            return default
        raise

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def append_json(path, new_data):
    """Ajoute un objet ou une liste d'objets à un fichier JSON existant."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Si new_data est un dictionnaire, on l'encapsule dans une liste
    if isinstance(new_data, dict):
        new_data = [new_data]

    data.extend(new_data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


        