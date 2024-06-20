import json

PROMPT = 'Повтори данный текст: <topic>'
try:
    file_path_prompt = 'N:\AI-Stream-Kit\Stream-Kit\controller\config\default.json'
    with open(file_path_prompt, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data['chatGpt']['dialoguePrompt'] = PROMPT
    with open(file_path_prompt, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Промпт успешно изменён на: {PROMPT}")
except FileNotFoundError as e:
    print('Ты не пряник( ', e)
