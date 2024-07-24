from pymongo import MongoClient
from myConfig import mongodb_address
from bson import ObjectId
client = MongoClient(mongodb_address)

# Выбор базы данных и коллекции
db = client['Director']
collection = db['Counter_topics_by_user']





# Создание нового пользователя
async def new_user(username, source, id):
    id = str(id)
    shema = {
        'username': username,
        'source': source,
        'id': id,
        'count': 0,
        'warnings': 0
    }
    collection.insert_one(shema)

async def block_user(source,name,tag,id):
    collection.delete_one({'id': id})
    BlackList = db['BlackList']
    BlackList.insert_one({'source': source, 'name': name, 'tag': tag, 'id': id})
    print(f'Пользователь {name}(@{tag}) был заблокирован')

# Увелечение счета пользователя (на 1)
async def add_count(username, source, id):
    id = str(id)
    result = collection.update_one({'id': id}, {'$inc': {'count': 1}})

    if result.matched_count:
        pass
    else:
        await new_user(username, source, id)
        await add_count(username, source, id)


async def add_warning(username,source,id):
    id = str(id)
    result = collection.update_one({'id': id}, {'$inc': {'warnings': 1}})
    if result.matched_count:
        pass
    else:
        await new_user(username,source,id)
        await add_warning(username,source,id)

async def warnings_by_user(username,source,id):
    id = str(id)
    try:
        warnings = collection.find_one({'id': id})['warnings']
        return warnings
    except TypeError:
        await new_user(username,source,id)
        await warnings_by_user(username,source,id)


async def search_nick(username,name_of_col,source,id):
    id = str(id)
    if name_of_col == 'BlackList':
        col = db[name_of_col]
        user = col.find_one({'id': id})
        if user:
            return True
        else: return False
    else:
        user = collection.find_one({'id': id})
        if user:
            pass
        else:
            await new_user(username,source,id)

async def sort_counter():
    # Получение и сохранение отсортированных документов
    sorted_documents = list(collection.find().sort('count', -1))

    if sorted_documents:
        collection.delete_many({})
        collection.insert_many(sorted_documents)

async def format_number(number):
    # Определяем масштабирование
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"  # Миллиарды
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"  # Миллионы
    elif number >= 1_000:
        return f"{number / 1_000:.0f}k"  # Тысячи
    else:
        return str(number)  # Меньше тысячи

