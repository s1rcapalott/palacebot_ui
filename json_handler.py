import json

    
def save_json(data, json_path):
    with open(json_path,"w") as json_file:
        json.dump(data, json_file, indent=4)
        return None
def load_expenses():
    pass
def load_checkouts():
    pass

