import pymongo
from pymongo import MongoClient
from myConfig import mongodb_address
import time

client = MongoClient(mongodb_address)

# Выбор базы данных и коллекции
db = client['Director']
collection = db['Counter_topics_by_user']


def sort_counter():
    # Получение и сохранение отсортированных документов
    sorted_documents = list(collection.find().sort('count', -1))

    # Удаление всех документов из коллекции, только если есть что удалять
    collection.delete_many({})
    for document in sorted_documents:
        document_id = collection.insert_one(document).inserted_id


# Создание нового пользователя
def new_user(username):
    shema = {
        'username': username,
        'count': 0
    }
    collection.insert_one(shema)


# Увелечение счета пользователя (на 1)
async def add_count(username):
    result = collection.update_one({'username': username}, {'$inc': {'count': 1}})

    if result.matched_count:
        pass
    else:
        new_user(username)
        await add_count(username)


# Удаление пользователя
def remove_user(username):
    collection.delete_one({'username': username})


def search_nick(username):
    user = collection.find_one({'username': username})
    if user:
        pass
    else:
        new_user(username)

# Добавление сценария в БД
def add_topic(db, requestor, source, priority, topic, style):
    while True:
        try:
            suggested_topic = {
                "type": "topic",
                "style": style,
                "requestor_id": requestor,
                "source": source,
                "priority": priority,
                "topic": topic
            }

            result = db.suggested_topics.insert_one(suggested_topic)
            print(
                "Запись с новой темой была успешно добавлена в suggested_topics. ID записи: " + str(result.inserted_id))
            break
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в generated_topics. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)


# Добавление мешапа в БД
def add_mashup(db, requestor, source, priority, speaker, url):
    while True:
        try:
            suggested_topic = {
                "type": "mashup",
                "requestor_id": requestor,
                "source": source,
                "priority": priority,
                "speaker": speaker,
                "url": url
            }

            result = db.suggested_topics.insert_one(suggested_topic)
            print("Запись с новым мешапом была успешно добавлена в suggested_topics. ID записи: " + str(
                result.inserted_id))
            break
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в generated_topics. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)


def connect_to_mongodb():
    while True:
        try:
            client = MongoClient(mongodb_address)
            database = client['Director']
            return database
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка установки соединения с mongodb. Продолжаем повторные попытки подключения...")
            print(e)
            time.sleep(1)
