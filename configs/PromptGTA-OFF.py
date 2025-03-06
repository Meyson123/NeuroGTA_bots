import json
import os
current_dir = os.path.dirname(__file__)

try:
    file_path_prompt = os.path.join(current_dir, '..', '..', '..', 'controller-gta', 'config', 'default.json')
    with open(file_path_prompt, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data['currentMode']['mode'] = "Off"
    with open(file_path_prompt, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Mode: Off")
except FileNotFoundError as e:
    print('Ты не пряник( ', e)
