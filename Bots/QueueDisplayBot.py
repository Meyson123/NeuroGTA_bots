import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb
# Путь к файлу, который будет читаться OBS
output_file = "QueueDisplayData.txt"



     
db = connect_to_mongodb()    
suggested = db["suggested_topics"]
generated = db["generated_topics"]

while True:
    try:
        # Получение количества записей в коллекции
        suggested_count = suggested.count_documents({})
        generated_count = generated.count_documents({})
        count = suggested_count + generated_count

        # Запись количества записей в файл
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"очередь: {count}\n")
        print(f"очередь: {count}\n")
        print()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Ожидание перед следующим обновлением
    time.sleep(10)  # обновление каждые 10 секунд
