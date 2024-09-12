import time
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb, add_interaction
# Путь к файлу, который будет читаться OBS
output_file = "QueueDisplayData.txt"



     
db = connect_to_mongodb()    
suggested = db["suggested_topics"]
generated = db["generated_topics"]

while True:
    try:
        # Получение количества записей в коллекции
        generated_count = generated.count_documents({"priority": {"$gt": 0}})
        suggested_count = suggested.count_documents({"priority": {"$gt": 0}})
        count = suggested_count + generated_count

        print(f"Очередь: {count}")
        asyncio.run(add_interaction(db, "queue", count))
        print("\n\n")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    # Ожидание перед следующим обновлением
    time.sleep(10)  # обновление каждые 10 секунд
