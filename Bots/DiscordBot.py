import time
import discord
from discord.ext import commands
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from myConfig import TopicDelay, MashupDelay, CanAddTopic, CanAddMashup, NeedTopicDelay, \
    NeedMashupDelay, NeedMashupDelayPerUser, TopicsChatName, MashupsChatName, AdminNames, valid_speakers, TopicPriority, \
    MashapPriority, replacements, default_topic_suggest_message, default_style, Project,threshold
from Mongodb.CountScripts import add_count, sort_counter,add_warning,block_user,search_nick,warnings_by_user
from Mongodb.BotsScripts import add_topic,connect_to_mongodb,filter,delete_theme,search_number,\
    get_topic_by_user,check_topic_exists, get_requestor_name_by_topic_id,add_mashup,replace_name
from TelegramSender import send_topic_to_telegram,send_similar_error,send_filter_error
load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Включение намерений для получения содержимого сообщений
source = "Discord"
mode = 'on'
last_topic_time = {}
last_mashup_time_per_user = {}
last_mashup_time_single = 0.0

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


db = connect_to_mongodb()


@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключен и готов к работе!')


@bot.event
async def on_message(message):
    global last_mashup_time_single
    global last_mashup_time_per_user
    global mode

    if message.author == bot.user:
        return
    topic = message.content[6:]
    message.content = message.content.lower()
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

            requestor_name = message.author.name
            requestor_id = message.author.id
            warnings = await warnings_by_user(requestor_name,source,requestor_id)
            check_result = await check_topic_exists(db, topic, threshold)
            if mode == 'off':
                await message.reply('Сожалеем,но прием тем на этом стриме уже завершен, ждем ваши темы на следующем.\n                                                        с любовью,Meyson')
                return
            if warnings == 5:
                await block_user(requestor_id)
            if await search_nick(requestor_name,'BlackList',source,requestor_id):
                await message.reply('Сожалеем,но вы заблокированы за нарушение правил. Вы можете подать заявку на разбан в https://discord.com/channels/1154075045149286470/1252310180037660762')
                return
            if await filter(topic):
                await add_warning(requestor_name,source,requestor_id)
                last_topic_time[requestor_id] = time.time()
                if warnings is None:
                    warnings = 0
                await message.reply( 'Ай-ай-ай,у нас тут так не принято. Не нужно кидать запрещенные темы\nО запрещенных темах можно узнать в https://discord.com/channels/1154075045149286470/1257244428947558460/1257269091035517000')
                await message.reply(f'На данный момент у вас {warnings+1} предупреждений.')
                await send_filter_error(topic,requestor_name,requestor_id,source,warnings+1)
                return
            if check_result[0]:
                procent, orig = check_result[1],check_result[2]
                await message.reply('Тема не добавлена!\nТакая тема(или подобная ей) уже есть в очереди.\nПридумайте что-нибудь другое')
                await send_similar_error(topic,requestor_name,requestor_id,source,orig,procent)
                return
            if "!стиль" in topic:
                style_content = topic.split("!стиль ", 1)[1]
                topic = topic.split("!стиль ", 1)[0].strip()
            else:
                style_content = default_style
            # topic_content = message.content[6:]  # Извлекаем содержимое темы из сообщения

            topic_id = await add_topic(db, requestor_name, requestor_id, source, TopicPriority, topic, style_content)  # Добавляем тему в БД
            await send_topic_to_telegram(topic, style_content, requestor_name, requestor_id, source, TopicPriority, str(topic_id))
            await add_count(message.author.name, source, requestor_id)
            await sort_counter()
            await message.reply(default_topic_suggest_message + f'\nТвоя позиция в очереди: {await search_number(topic_id,db)}', mention_author=False)

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
                        if message.author.name in last_mashup_time_per_user and time.time() - last_mashup_time_per_user[
                            message.author.name] < MashupDelay:
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
                if speaker in valid_speakers:
                    eng_speaker = replace_name(speaker, replacements)
                    await add_mashup(db, message.author.name, "Discord", MashapPriority, eng_speaker, url)
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
    elif message.content.startswith('!off'):
        mode = 'off'
    await bot.process_commands(message)







print('Запуск ДС бота...')

if Project == 'Gta':
    bot.run(os.getenv('TOKENDSGTA'))
else:
    bot.run(os.getenv('TOKENDSSMESH'))
