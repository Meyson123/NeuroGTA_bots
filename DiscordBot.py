import time
import re
import pymongo
from pymongo import MongoClient
import discord
from discord.ext import commands
import sys
import os
from dotenv import load_dotenv
from myConfig import mongodb_address, TopicDelay, MashupDelay, CanAddTopic, CanAddMashup, NeedTopicDelay, \
    NeedMashupDelay, NeedMashupDelayPerUser, TopicsChatName, MashupsChatName, AdminNames, valid_speakers, TopicPriority, \
    MashapPriority, replacements, default_topic_suggest_message, default_style

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Включение намерений для получения содержимого сообщений

last_topic_time = {}
last_mashup_time_per_user = {}
last_mashup_time_single = 0.0

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

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


@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключен и готов к работе!')


@bot.event
async def on_message(message):
    global last_mashup_time_single
    global last_mashup_time_per_user

    if message.author == bot.user:
        return

    channel_name = message.channel.name
    # print(f"Сообщение пришло из чата с названием: {channel_name}")

    if message.content.startswith('!тема'):
        if not channel_name in TopicsChatName:
            return
        if not CanAddTopic:
            return

        try:
            if not (message.author.name in AdminNames):
                if NeedTopicDelay:
                    # Проверяем, есть ли пользователь в словаре и прошла ли минута с момента последнего добавления темы
                    if message.author.name in last_topic_time and time.time() - last_topic_time[
                        message.author.name] < TopicDelay:
                        minuta = "минуту" if TopicDelay / 60 == 1 else (
                            "минуты" if 2 <= TopicDelay / 60 <= 4 else "минут")
                        await message.reply(
                            f"Вы можете добавить тему не чаще, чем раз в {int(TopicDelay / 60)} {minuta}.")
                        return

            topic_content = message.content.split("!тема ", 1)[1]
            if "!стиль" in topic_content:
                style_content = topic_content.split("!стиль ", 1)[1]
                topic_content = topic_content.split("!стиль ", 1)[0].strip()
            else:
                style_content = default_style
            # topic_content = message.content[6:]  # Извлекаем содержимое темы из сообщения
            requestor = message.author.name  # Имя автора сообщения
            source = "Discord"

            add_topic(db, requestor, source, TopicPriority, topic_content, style_content)  # Добавляем тему в БД

            await message.reply(default_topic_suggest_message, mention_author=False)

            # Обновляем время последнего добавления темы для пользователя
            last_topic_time[message.author.name] = time.time()
        except IndexError:
            await message.reply('Пожалуйста, укажите тему после команды !тема', mention_author=False)

    elif message.content.startswith('!мэшап'):
        if channel_name != MashupsChatName:
            return
        if not CanAddMashup:
            return

        try:
            if not (message.author.name in AdminNames):
                if NeedMashupDelay:
                    # Если задержка по юзеру
                    if NeedMashupDelayPerUser:
                        # Проверяем, есть ли пользователь в словаре и прошла ли минута с момента последнего добавления темы
                        if message.author.name in last_mashup_time_per_user and time.time() - last_mashup_time_per_user[message.author.name] < MashupDelay:
                            minuta = "минуту" if MashupDelay / 60 == 1 else (
                                "минуты" if 2 <= MashupDelay / 60 <= 4 else "минут")
                            await message.reply(
                                f"Вы можете добавить мэшап не чаще, чем раз в {int(MashupDelay / 60)} {minuta}.")
                            return
                    # Если задержка общая
                    else:
                        if time.time() - last_mashup_time_single < MashupDelay:
                            minuta = "минуту" if MashupDelay / 60 == 1 else (
                                "минуты" if 2 <= MashupDelay / 60 <= 4 else "минут")
                            await message.reply(
                                f"В экспериментальном режиме работает общая задержка на всех юзеров. Мэшап может быть добавлен не чаще чем раз в {int(MashupDelay / 60)} {minuta}.")

                            sec_ost = MashupDelay - (time.time() - last_mashup_time_single)
                            min_ost = int(sec_ost / 60) + 1
                            minuta_ost_text = "минута" if min_ost == 1 else ("минуты" if 2 <= min_ost <= 4 else "минут")

                            await message.reply(
                                f"До возможности добавить следующий мэшап: {min_ost} {minuta_ost_text}.")
                            return

            mashup = message.content.split("!мэшап ", 1)[1]

            if mashup and " " in mashup:
                speaker, url = mashup.split(" ", 1)
                if not (url.startswith('https://www.youtube.com/watch?v=')):
                    await message.reply(
                        'Используйте ссылку на видео на Ютубе, начинающуюся с https://www.youtube.com/watch?v=',
                        mention_author=False)
                    return;
                if (speaker in valid_speakers):
                    eng_speaker = replace_name(speaker, replacements)
                    add_mashup(db, message.author.name, "Discord", MashapPriority, eng_speaker, url)
                    await message.reply('Мэшап добавлен в книжечку!', mention_author=False)

                    # Обновляем время последнего добавления мэшапа
                    if NeedMashupDelayPerUser:
                        last_mashup_time_per_user[message.author.name] = time.time()
                    else:
                        last_mashup_time_single = time.time()
                else:
                    print("Ошибка верификации голоса.")
                    speakers_list = ', '.join(valid_speakers)
                    await message.reply(f'Пожалуйста, используйте имя из списка: {speakers_list}', mention_author=False)
            else:
                print("Неверный формат запроса")
                await message.reply('Пожалуйста используйте формат: !мэшап <Имя> <Ссылка>', mention_author=False)
        except IndexError:
            await message.reply('Пожалуйста используйте формат: !мэшап <Имя> <Ссылка>', mention_author=False)

    await bot.process_commands(message)


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


def replace_name(name, replacements):
    for old, new in replacements:
        if name == old:
            return new
    return name


bot.run(os.getenv('TOKENDS'))
