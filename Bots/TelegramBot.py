import asyncio
import os
import sys
import time
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from telebot.async_telebot import AsyncTeleBot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myConfig import mongodb_address, AdminTgIds, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message, default_style

from Mongodb.BDScripts import add_count, sort_counter,add_topic,connect_to_mongodb

load_dotenv()
bot = AsyncTeleBot(os.getenv('TOKENTG'))

last_topic_time = {}





# Функция подключения к mongodb


db = connect_to_mongodb()


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, 'Wassup, nigga🖐️\n'
                                            'Здесь ты можешь предложить тему на стрим Нейро GTA.\n'
                                            '/topic - задать тему\n'
                                            '/help - для подробной информации')


# Сообщение с информацией
@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, 'Все до жути просто, братан. Просто пиши команду "/topic", а дальше свою тему\n\n'
                                            "Также по желанию можно добавить истории свой стиль(жанр), для этого нужно после темы добавить команду !стиль [Свой стиль]\n"
                                            'Пример: "/topic CJ и Smoke осознали что ими управляет нейросеть !стиль хоррор"\n\n'
                                            "PS. В нашем дискорд сервере задержка на добавление темы меньше). Секретная ссылка на наш дискорд: https://discord.gg/HcfJw5umC3\n"
                                            "Pss. Только никому🤫")


# Передача тем от бота
@bot.message_handler(commands=['topic'])
async def topic(message):
    if message.text[6:] == '':
        await bot.send_message(message.chat.id, 'Тема не может быть пустой. Пожалуйста, напиши свою тему сразу после команды /topic')
    else:
        user_topic = message.text[6:]
        requestor = message.from_user.first_name
        sourse = 'Telegram'
        if not (message.chat.id in AdminTgIds):
            if NeedTopicDelay:
                # Проверяем, есть ли пользователь в словаре и прошлo ли 2 минуты с момента последнего добавления темы
                if message.chat.id in last_topic_time and time.time() - last_topic_time[message.chat.id] < TopicDelayTg:
                    minuta = "минуту" if TopicDelayTg / 60 == 1 else (
                        "минуты" if 2 <= TopicDelayTg / 60 <= 4 else "минут")
                    await bot.reply_to(message,
                                       f"Ты можешь добавить тему не чаще, чем раз в {int(TopicDelayTg / 60)} {minuta}.")
                    return
        if "!стиль" in user_topic:
            style_content = user_topic.split("!стиль ", 1)[1]
            user_topic = user_topic.split("!стиль ", 1)[0].strip()
        else:
            style_content = default_style
        await add_topic(db, requestor, sourse, TopicPriority, user_topic, style_content)
        await bot.send_message(-1002175092872, f'''
                                                    Тема: {topic}
                                                    Стиль: {style_content}
                                                    Ник автора: {requestor}
                                                    Приоритет: {TopicPriority}''')
        await bot.reply_to(message, text=default_topic_suggest_message)
        add_count(message.from_user.first_name)
        sort_counter()
    last_topic_time[message.chat.id] = time.time()

@bot.message_handler()
async def send_text(message):
    await bot.send_message(message.chat.id, "Бро, задай тему с помощью команды /topic, или посмотри подробности с помощью /help")


print('Запуск ТГ бота...')

asyncio.run(bot.polling(skip_pending=True))
