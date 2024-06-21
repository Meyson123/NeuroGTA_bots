from pymongo import MongoClient
from myConfig import mongodb_address

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



