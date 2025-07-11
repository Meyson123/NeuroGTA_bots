from pymongo import MongoClient
import pymongo
import time
from myConfig import mongodb_address, default_style
import re
from fuzzywuzzy import fuzz
from bson import ObjectId

ban_words = [
    'дети', 'детей', 'детям', 'детьми', 'детях',
    'кокаин', 'героин', 'марихуана', 'амфетамин', 'экстази',
    'Сирия', 'Афганистан', 'Ирак', 'Украина', 'Ливия',
    'метамфетамин', 'пропан', 'лизергиновая кислота','мет','меф',
    'Сирия', 'Афганистан', 'Ирак', 'Украина', 'Ливия', 'Сомали', 'Йемен', 'Судан', 'Северная Корея',
    'девочка', 'девочки', 'девочке', 'девочку', 'девочкой', 'девочках',
    'мальчик', 'мальчика', 'мальчику', 'мальчиком', 'мальчике',
    'ребенок', 'ребенка', 'ребенку', 'ребенком', 'ребенке', 'дети',
    'Путин', 'Путина', 'Путину', 'Путиным', 'Путине',
    'Россия', 'России', 'Россию', 'Россией',
    'Украина', 'Украины', 'Украине', 'Украину', 'Украиной',
    'специальная военная операция', 'специальной военной операции', 'специальную военную операцию',
    'специальной военной операцией', 'сво', 'Гитлер', 'Гитлера', 'Гитлеру', 'Гитлером', 'Гитлере', 'Рейх',
    'украинскую', 'украинской', 'детскую', 'детской', 'геноцид', 'геноцида', 'геноциду', 'геноцидом', 'геноциде',
    'евреев', 'еврею', 'евреем', 'еврей', 'ислам', 'ислама', 'исламу', 'исламом', 'исламе', 'детишки', 'детишек', 
    'детишкам', 'детишками', 'детишках', 'Навальный', 'Навального', 'Навальному', 'Навальным', 'Навальном', 'зигу', 'зига']


async def add_topic(db, requestor_name,user_tag,requestor_id, source, priority, topic, style):
    while True:
        try:
            suggested_topic = {
                "type": "topic",
                "style": style,
                "requestor_name": requestor_name,
                "user_tag": user_tag,
                "requestor_id": requestor_id,
                "source": source,
                "priority": priority,
                "additionally": "",
                "topic": topic
            }

            result = db.suggested_topics.insert_one(suggested_topic)
            print(
                "Запись с новой темой была успешно добавлена в suggested_topics. ID записи: " + str(result.inserted_id))
            return result.inserted_id
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в generated_topics. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)
    pass


async def add_interaction(db, action, parameter):
    while True:
        try:
            action_topic = {
                "action": action,
                "parameter": parameter
            }

            result = db.interactions.insert_one(action_topic)
            print(
                "Запись с новым действием была успешно добавлена в interactions. ID записи: " + str(result.inserted_id))
            return result.inserted_id
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в interactions. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)
    pass


# Добавление мешапа в БД
async def add_mashup(db, requestor_name,requestor_id, source, priority, speaker, url):
    while True:
        try:
            suggested_topic = {
                "type": "mashup",
                "requestor_name": requestor_name,
                "requestor_id": requestor_id,
                "source": source,
                "priority": priority,
                "speaker": speaker,
                "url": url
            }

            result = db.suggested_topics.insert_one(suggested_topic)
            print("Запись с новым мешапом была успешно добавлена в suggested_topics. ID записи: " + str(result.inserted_id))
            break
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в generated_topics. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)


async def edit_topic(db, message):
    topic, style = await check_topic_style(message)
    col = db["suggested_topics"]
    doc = col.find_one()

    if topic == "":
        topic = doc["topic"]
    if style == default_style and doc["style"] != default_style:
        style = doc["style"]

    id = doc["_id"]
    result = col.update_one(
        {"_id": id},
        {'$set': {'topic': topic, 'style': style}}
    )
    return result.modified_count > 0
    


async def filt(topic):
    topic_words = topic.split()
    for word in ban_words:
        for topic_word in topic_words:
            if word.lower() == topic_word.lower():
                return True
    return False


async def check_topic_style(topic):
    pattern = r'! ?стиль (.+)'
    match = re.search(pattern, topic, re.IGNORECASE)
    if match:
        style_content = match.group(1)
        topic = re.sub(pattern, '', topic, flags=re.IGNORECASE).strip()
    else:
        style_content = default_style
    return topic, style_content


async def check_topic_exists(db, topic, threshold):
    collection = db['suggested_topics']
    cursor = collection.find({}, {"topic": 1, "_id": 0})
    
    # Поиск темы с достаточным уровнем совпадения
    for entry in cursor:
        stored_topic = entry.get("topic", "")
        similarity = fuzz.partial_ratio(topic.lower(), stored_topic.lower())
        if similarity >= threshold:
            return [True, similarity,stored_topic]
    
    return [False]


async def delete_theme(db, topic_id):
    collection = db['suggested_topics']
    document = collection.find_one({"_id": ObjectId(topic_id)})
    topic = document['topic']
    if document:
        collection.delete_one({"_id": document["_id"]})
        print(f"Тема '{topic}' успешно удалена из suggested_topics.")
    else:
        print(f"Тема '{topic}' не найдена в suggested_topics.")


async def up_theme(db, topic_id):
    collection = db['suggested_topics']
    document = collection.update_one({'_id': ObjectId(topic_id)}, {'$inc': {'priority': 1}})


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


async def search_number(topic_id, db):
    suggested = db["suggested_topics"]
    generated = db["generated_topics"]

    document = generated.find_one({"_id": ObjectId(topic_id)})

    if document:
        # Получаем порядковый номер документа в коллекции generated_topics
        document_number = generated.count_documents({'_id': {'$lt': document['_id']}, 'priority': {'$gt': 0}}) + 1
        return document_number
    else:
        document = suggested.find_one({"_id": ObjectId(topic_id)})

        if document:
            # Получаем порядковый номер документа в коллекции suggested_topics
            document_number = suggested.count_documents({'_id': {'$lt': document['_id']}}) + 1 - generated.count_documents({'priority': 0})
            return document_number + generated.count_documents({})

    return None

async def get_members_id(db):
    collection = db["Counter_topics_by_user"]
    all_id = []
    for member in list(collection.find({'source': 'Telegram'})):
        all_id.append(member['id'])
    return all_id


async def get_topic_by_user(id, db):
    suggested = db["suggested_topics"]
    generated = db["generated_topics"]
    return list(generated.find({'requestor_id':id})) + list(suggested.find({'requestor_id':id}))


async def get_parameters_by_topic_id(db, topic_id, *parameters):
    try:
        document = db["suggested_topics"].find_one({"_id": ObjectId(topic_id)})
        if document:
            info = tuple(document.get(param) for param in parameters)
            return info
        else:
            print(f"Документ с _id '{topic_id}' не найден в коллекции 'suggested_topics'.")
            return None
    except pymongo.errors.PyMongoError as e:
        print(f"Ошибка при поиске информации по _id '{topic_id}' в коллекции 'suggested_topics': {e}")
        return None


async def get_id_by_theme_number(db,number):
    document = db['generated_topics'].find().skip(number).limit(1)
    if document:
        for doc in document:
            if doc['source'] == 'Telegram':
                id = doc['requestor_id']
                return id
            return 0
    return 0


def replace_name(name, replacements):
    for old, new in replacements:
        if name == old:
            return new
    return name
