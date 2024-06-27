from pymongo import MongoClient
import time
from myConfig import mongodb_address, QueueGeneratedText, QueueSuggestedText

# Путь к файлу, который будет читаться OBS
output_file = "QueueDisplayData.txt"


# Функция подключения к mongodb
def connect_to_mongodb():
    while True:
        try:
            client = MongoClient(mongodb_address)
            db = client['Director']
            return db
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка установки соединения с mongodb. Продолжаем повторные попытки подключения...")
            print(e)
            time.sleep(1)
     
db = connect_to_mongodb()    
suggested = db["suggested_topics"]
generated = db["generated_topics"]

while True:
    try:
        # Получение количества записей в коллекции
        suggested_count = suggested.count_documents({})
        generated_count = generated.count_documents({})
        
        # Запись количества записей в файл
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{QueueSuggestedText} {suggested_count}\n")
            f.write(f"{QueueGeneratedText} {generated_count}")
        print(f"{QueueSuggestedText} {suggested_count}")
        print(f"{QueueGeneratedText} {generated_count}")
        print()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Ожидание перед следующим обновлением
    time.sleep(5)  # обновление каждые 10 секунд
