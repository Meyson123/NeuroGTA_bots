import os
import sys
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb

destination_folder = r'N:\AI-Stream-Kit\Ads'  

db = connect_to_mongodb()

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

def process_document(document, collection):
    id = str(document['_id'])
    document_folder = os.path.join(destination_folder, id)
    
    if not os.path.exists(document_folder):
        os.makedirs(document_folder)
    
        for idx, item in enumerate(document.get('scenario', [])):
            sound_path = item.get('sound')
            
            if sound_path and os.path.exists(sound_path):
                # Получаем имя файла
                filename = os.path.basename(sound_path)
                # Создаем уникальную папку для каждого звука внутри папки документа
                sound_folder = os.path.join(document_folder, f'sound_{idx}')
                
                if not os.path.exists(sound_folder):
                    os.makedirs(sound_folder)
                
                # Новый путь к файлу внутри уникальной папки для звука
                new_path = os.path.join(sound_folder, filename)
                # Копируем файл
                shutil.copy2(sound_path, new_path)
                # Обновляем путь в документе
                item['sound'] = new_path
            else:
                print(f"Error: {sound_path} не найден")
                return
        print(f'Документ {id} перенесен в папку {sound_path}.')
    else:
        print(f'Документ {id} уже есть в папке.')
    
    # Обновляем документ в коллекции
    collection.update_one(
        {"_id": document["_id"]},
        {"$set": {"scenario": document['scenario']}}
    )

def save_to_disk(collection):
    for document in collection.find():
        process_document(document, collection)
    print("Файлы скопированы в уникальные папки, и пути обновлены.\n")
   
    print("Удалить все звуки из Temp?")
    user_input = input("Введите 'y' для подтверждения: ")
    if user_input.lower() == 'y':
        temp_folder = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'Gradio')
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
            print("Файлы из Temp удалены.")
        else:
            print("Папка Temp не найдена.")
    else:
        print("Удаление отменено.")

save_to_disk(db["ads"])
