import asyncio
import os
import time
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from telebot.async_telebot import AsyncTeleBot

from myConfig import mongodb_address, AdminTgIds, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message, default_style

from CounterScripts import add_count, sort_counter

load_dotenv()
bot = AsyncTeleBot(os.getenv('TOKENTG'))

last_topic_time = {}





# Функция подключения к mongodb
def connect_to_mongodb():
    while True:
        try:
            client = MongoClient(mongodb_address)
            db = client['Director']
            return db
        except pymongo.errors.AutoReconnect as e:
            print_colored_message(f"Ошибка установки соединения с mongodb. Продолжаем повторные попытки подключения...")
            print(e)
            time.sleep(1)


db = connect_to_mongodb()


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, 'Wassup,nigga🖐️ Здесь ты можешь предложить тему на стрим NeuroGta.\n'
                                            '/help - для подробной информации')


# Сообщение с информацией
@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, "Все до жути просто,братан. Просто пиши '''/тема''' а дальше свою тему\n"
                                            "Также можно добавить истории свой стиль(жанр),для этого нужно после своей темы добавить !стиль [Свой стиль]\n"
                                            "Пример: '/тема Cj и Smoke осознали что ими управляет нейросеть !стиль хоррор'\n"
                                            "Ps. В нашем дискорд сервере задержка на добавление темы меньше). Секретная ссылка на наш дискорд: https://discord.gg/Eqc38NT7tr\n"
                                            "Pss. Только никому🤫")


# Передача тем от бота
@bot.message_handler(commands=['topic'])
async def topic(message):
    if message.text[6:] == '':
        await bot.send_message(message.chat.id, 'Тема не может быть пустой')
    else:
        user_topic = message.text[6:]
        requester = message.from_user.first_name
        sourse = 'Telegram'
        if not (message.chat.id in AdminTgIds):
            if NeedTopicDelay:
                # Проверяем, есть ли пользователь в словаре и прошлo ли 2 минуты с момента последнего добавления темы
                if message.chat.id in last_topic_time and time.time() - last_topic_time[message.chat.id] < TopicDelayTg:
                    minuta = "минуту" if TopicDelayTg / 60 == 1 else (
                        "минуты" if 2 <= TopicDelayTg / 60 <= 4 else "минут")
                    await bot.reply_to(message,
                                       f"Вы можете добавить тему не чаще, чем раз в {int(TopicDelayTg / 60)} {minuta}.")
                    return
        if "!стиль" in user_topic:
            style_content = user_topic.split("!стиль ", 1)[1]
            user_topic = user_topic.split("!стиль ", 1)[0].strip()
        else:
            style_content = default_style
        await add_topic(db, requester, sourse, TopicPriority, user_topic, style_content)
        await add_count(message.from_user.first_name)
        sort_counter()
        await bot.reply_to(message, text=default_topic_suggest_message)
    last_topic_time[message.chat.id] = time.time()


# Отправка темы в Бд
async def add_topic(db, requestor, source, priority, topic, style):
    await bot.send_message(-1002175092872, f'''
Тема: {topic}
Стиль: {style}
Ник автора: {requestor}
Приоритет: {priority}''')
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
            print("Запись с новой темой была успешно добавлена в suggested_topics. ID записи: " + str(
                result.inserted_id))
            break
        except pymongo.errors.AutoReconnect as e:
            print(f"Ошибка добавления записи в generated_topics. Продолжаем повторные попытки отправки запроса...")
            print(e)
            time.sleep(1)


print('Запуск ТГ бота...')

asyncio.run(bot.polling(skip_pending=True))
