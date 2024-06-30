from pymongo import MongoClient
import pymongo
import time
from myConfig import mongodb_address
import re

ban_words = [
    'дети', 'детей', 'детям', 'детьми', 'детях',
    'кокаин', 'героин', 'марихуана', 'амфетамин', 'экстази',
    'Сирия', 'Афганистан', 'Ирак', 'Украина', 'Ливия',
    'метамфетамин', 'пропан', 'лизергиновая кислота','мет','меф',
    'Сирия', 'Афганистан', 'Ирак', 'Украина', 'Ливия', 'Сомали', 'Йемен', 'Судан', 'Северная Корея',
    'девочка', 'девочки', 'девочке', 'девочку', 'девочкой', 'девочках',
    'мальчик', 'мальчика', 'мальчику', 'мальчиком', 'мальчике',
    'ребенок', 'ребенка', 'ребенку', 'ребенком', 'ребенке', 'дети',
    'сво','Россия'
]

async def add_topic(db, requestor, source, priority, topic, style):
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
    pass


# Добавление мешапа в БД
async def add_mashup(db, requestor, source, priority, speaker, url):
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


async def filter(topic):
    for word in ban_words:
        if word.lower() in topic.lower():
            return True
    return False


async def delete_theme(db, topic):
    collection = db['suggested_topics']
    document = collection.find_one({"topic": topic})
    if document:
        collection.delete_one({"_id": document["_id"]})
        print(f"Тема '{topic}' успешно удалена из suggested_topics.")
    else:
        print(f"Тема '{topic}' не найдена в suggested_topics.")

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

async def search_number(topic,db):
    suggested = db["suggested_topics"]
    generated = db["generated_topics"]
    document = suggested.find_one({'topic': topic})
    if document:
        # Получаем порядковый номер документа в коллекции
        document_number = len(list(suggested.find({'_id': document['_id']}))) + 1
        return document_number + generated.count_documents({})
    else:
        document = generated.find_one({'topic': topic})
        if document:
            document_number = len(list(suggested.find({'_id': {'$lt': document['_id']}}))) + 1
            return document_number
async def get_topic_by_user(username,db):
    suggested = db["suggested_topics"]
    generated = db["generated_topics"]
    all_topics = []
    for sug_topic in list(suggested.find({'requestor_id':username})):
        all_topics.append(sug_topic['topic'])
    for gen_topic in list(generated.find({'requestor_id':username})):
        all_topics.append(gen_topic['topic'])
    return all_topics


def replace_name(name, replacements):
    for old, new in replacements:
        if name == old:
            return new
    return name
