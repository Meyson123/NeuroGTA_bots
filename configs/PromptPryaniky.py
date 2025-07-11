import json
import os
current_dir = os.path.dirname(__file__)

PROMPT = "Создай беседу между Смешариками не более 1 минуты. Доступные персонажи и их характеры: {Крош: Весёлый и энергичный кролик, Любимая фраза - Ёлки-Иголки! / Ёжик: Застенчивый ёж, добрый, нерешительный, тихий, обожает коллекционирование, дружит с Крошем. Любимая фраза: Так сказать…. / Бараш: Сентиментальный меланхоличный баран, романтик, лирик, поэт, обожает горы, влюблён в Нюшу. Любимая фраза: Ох! / Нюша: Свинка-модница, очень эмоциональная, мечтательная, требует внимания, манипулирует мальчиками, Любимая фраза: Держите меня, я падаю…/ Карыч: Пожилой ворон, артист, музыкант, фантазёр, Любимая фразы: Мамма мия!./ Лосяш: Интеллигентный лось-учёный, спокойный, гений, реалист, Любимая фраза: Феноменально!}. Если в теме указан персонаж которого нет в списке, его имя тоже можешь использовать. Текст нужно отформатировать как \"Имя\": \"Реплика\". Стиль беседы: <style>. Тема: <topic>. Используй обязательно русский язык."
try:
    file_path_prompt = os.path.join(current_dir, '..', '..', '..', 'controller', 'config', 'default.json')
    with open(file_path_prompt, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data['chatGpt']['dialoguePrompt'] = PROMPT
    with open(file_path_prompt, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Промпт успешно изменён на: {PROMPT}")
except FileNotFoundError as e:
    print('Ты не пряник( ', e)
