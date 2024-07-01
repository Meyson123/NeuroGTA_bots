import asyncio
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot, types
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
from myConfig import AdminTgIds, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message, default_style,threshold
from Mongodb.CountScripts import warnings_by_user,add_count, sort_counter,add_warning,block_user,search_nick
from Mongodb.BotsScripts import add_topic,connect_to_mongodb,filter,delete_theme,search_number,\
    get_topic_by_user,check_topic_exists, get_requestor_name_by_topic_id


load_dotenv()
bot = AsyncTeleBot(os.getenv('TOKENTG'))
mode = 'on'
last_topic_time = {}


# Функция подключения к mongodb
db = connect_to_mongodb()
source = 'Telegram'

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
    topic = message.text[7:]
    requestor_name = message.from_user.first_name
    requestor_id = message.from_user.id
    warnings = await warnings_by_user(requestor_id)
    if mode == 'off':
        await bot.send_message(message.chat.id,'Сожалеем,но прием тем на этом стриме уже завершен, ждем ваши темы на следующем.\n -с любовью,Meyson')
        await bot.send_sticker(message.chat.id,'CAACAgIAAxkBAAEMZ-JmgY_WuGvpBWdSmJ99nMQgy7qMqQACBxkAAs0xEEghvxdEJ73qJDUE')
        return
    if warnings == 5:
        await block_user(requestor_id)
    if await search_nick(requestor_name,'BlackList',source,requestor_id):
        await bot.send_message(message.chat.id,'Сожалеем,но вы заблокированы за нарушение правил. Вы можете попробовать вымолить прощение у @Meyson420')
        return
    if topic == '' or topic == 'NeuroGta_bot':
        await bot.send_message(message.chat.id, 'Тема не может быть пустой. Пожалуйста, напиши свою тему сразу после команды /topic')
        return
    if await filter(topic):
        await add_warning(requestor_name,source,requestor_id)
        last_topic_time[requestor_id] = time.time()
        await bot.send_message(message.chat.id, 'Ай-ай-ай,у нас тут так не принято. Не нужно кидать запрещенные темы\n/ban_themes - Запрещенные темы')
        await bot.send_message(message.chat.id,f'На данный момент у вас {warnings} предупреждений.')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban|&|{requestor_id}"))
        await bot.send_message(-1002175092872, f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Количество предупреждений: {warnings}''',reply_markup=markup)
        return
    check_result = await check_topic_exists(db, topic, threshold)
    if check_result[0]:
         procent, orig = check_result[1],check_result[2]
         await bot.send_message(message.chat.id, 'Тема не добавлена!\nТакая тема(или подобная ей) уже есть в очереди.\nПридумайте что-нибудь другое')
         await bot.send_message(-1002175092872, f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Оригинальная тема: {orig}
Процент сходства: {procent}%''')
         return
    if not (message.chat.id in AdminTgIds):
        if NeedTopicDelay:
            # Проверяем, есть ли пользователь в словаре и прошло ли 2 минуты с момента последнего добавления темы
            if message.chat.id in last_topic_time and time.time() - last_topic_time[message.chat.id] < TopicDelayTg:
                minuta = "минуту" if TopicDelayTg / 60 == 1 else (
                    "минуты" if 2 <= TopicDelayTg / 60 <= 4 else "минут")
                await bot.reply_to(message,
                                   f"Ты можешь добавить тему не чаще, чем раз в {int(TopicDelayTg / 60)} {minuta}.")
                return
    if "!стиль" in topic:
        style_content = topic.split("!стиль ", 1)[1]
        topic = topic.split("!стиль ", 1)[0].strip()
    else:
        style_content = default_style
    topic_id = await add_topic(db, requestor_name,requestor_id, source, TopicPriority, topic, style_content)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🗑 Удалить тему', callback_data=f"del|&|{requestor_id}|&|{topic_id}"))
    markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban|&|{requestor_id}|&|{topic_id}"))
    await bot.send_message(-1002175092872, f'''
Тема: {topic}
Стиль: {style_content}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Приоритет: {TopicPriority}''',reply_markup=markup)
    await bot.reply_to(message, text=default_topic_suggest_message + f'\nТвоя позиция в очереди: {await search_number(topic_id,db)}\n\nЧтобы посмотреть свою текущую позицию в очереди, используй команду:\n/queue')
    await add_count(requestor_name, source, str(requestor_id))
    await sort_counter()
    last_topic_time[requestor_id] = time.time()

@bot.message_handler(commands=['ban_themes'])
async def ban_themes(message):
    await bot.send_message(message.chat.id,'''У нас на стриме запрещены темы связанные с:
1)Политикой
2)Детьми
3)Алкоголем,никотиносодержащими изделиями(сигареты и тп),наркотиками(прямым упоминанием веществ)
Пока все,но лишний раз баловаться не нужно''')

@bot.message_handler(commands=['queue'])
async def queue(message):
    user_id = message.from_user.id
    k = 1
    spisok = ''
    for topics in await get_topic_by_user(user_id,db):
        number = await search_number(topics['_id'],db)
        topic = topics['topic']
        spisok = spisok + f'{k}) {topic} - {number} место в очереди\n'
        k += 1
    await bot.send_message(message.chat.id,f'{spisok}\nP.S. Если до твоей темы далеко - за 25₽ можно заказать тему без очереди!\nhttps://www.donationalerts.com/r/neuro_gta')

@bot.callback_query_handler(func=lambda call: True)
async def del_theme(call):
    calldata = call.data.split('|&|')
    but = calldata[0]
    user_id = calldata[1]
    if but == 'del':
        topic_id = calldata[2]
        user_name = await get_requestor_name_by_topic_id(topic_id, db)
        await delete_theme(db,topic_id)
        await add_warning(user_name,source,user_id)
        await bot.reply_to(call.message,'Тема удалена, +1 предупреждение')
    elif but == 'ban':
        await block_user(user_id)
        await bot.reply_to(call.message,'Пользователь заблокирован. Ебать он лох')

@bot.message_handler(commands='off')
async def off(message):
    if not(message.chat.id in AdminTgIds):
        return
    global mode
    mode = 'off'

@bot.message_handler()
async def send_text(message):
    if not(message.chat.id in AdminTgIds):
        if mode == 'on':
           await bot.send_message(message.chat.id, "Бро, задай тему с помощью команды /topic, или посмотри подробности с помощью /help")
        else: 
            await bot.send_message(message.chat.id,'Сожалеем,но прием тем на этом стриме уже завершен, ждем ваши темы на следующем.\n    - с любовью,Meyson')
            await bot.send_sticker(message.chat.id,'CAACAgIAAxkBAAEMZ-JmgY_WuGvpBWdSmJ99nMQgy7qMqQACBxkAAs0xEEghvxdEJ73qJDUE')



print('Запуск ТГ бота...')

asyncio.run(bot.polling(skip_pending=True))
