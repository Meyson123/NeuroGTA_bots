import json
import os
current_dir = os.path.dirname(__file__)

def change_language(language):
    try:
        file_path_prompt = os.path.join(current_dir, '..', '..', '..', 'controller', 'config', 'default.json')
        with open(file_path_prompt, 'r', encoding='utf-8') as file:
            data = json.load(file)
        data['chatGpt']['dialoguePrompt'] = data['chatGpt']['dialoguePromptRU'] if language == "ru" else data['chatGpt']['dialoguePromptEN']
        with open(file_path_prompt, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Язык успешно изменен на: {language}")
    except FileNotFoundError as e:
        print('Ты не пряник( ', e)

    try:
        file_path_gateaway = os.path.join(current_dir, '..', '..', '..', 'rvc', '_gateway.py')  
        with open(file_path_gateaway, 'r', encoding='utf-8') as file:
            file_contents = file.read()
        if language == "en":
            new_contents = file_contents.replace("current_language = 'ru'", "current_language = 'en'")
        else:
            new_contents = file_contents.replace("current_language = 'en'", "current_language = 'ru'")
        with open(file_path_gateaway, 'w', encoding='utf-8') as file:
            file.write(new_contents)
    except FileNotFoundError as e:
        print('Ты не пряник( ', e)

