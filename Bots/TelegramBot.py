import asyncio
import os
import time

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot, types
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton

from myConfig import AdminTgIds, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message, default_style

from Mongodb.CountScripts import add_count, sort_counter,add_warning,block_user,search_nick
from Mongodb.BotsScripts import add_topic,connect_to_mongodb,filter,delete_theme,search_number,get_topic_by_user
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
    user_topic = message.text[7:]
    requestor = message.from_user.first_name
    source = 'Telegram'
    if await search_nick(requestor,'BlackList'):
        await bot.send_message(message.chat.id,'Сожалеем,но вы заблокированы за нарушение правил. Вы можете попробовать вымолить прощение у @Meyson420')
        return
    if user_topic == '' or user_topic == 'NeuroGta_bot':
        await bot.send_message(message.chat.id, 'Тема не может быть пустой. Пожалуйста, напиши свою тему сразу после команды /topic')
        return
    if await filter(user_topic):
        warnings = await add_warning(requestor)
        await bot.send_message(message.chat.id, 'Ай-ай-ай,у нас тут так не принято. Не нужно кидать запрещенные темы\n /ban_themes - Запрещенные темы')
        await bot.send_message(message.chat.id,f'На данный момент у вас {warnings} предупреждений.')
        await bot.send_message(-1002175092872, f'''
Тема: {user_topic}
Ник автора: {requestor}
Количество предупреждений: {warnings}
Тема заблокирована''')
        return
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
    await add_topic(db, requestor, source, TopicPriority, user_topic, style_content)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🗑 Удалить тему', callback_data=f"delete_theme {requestor} {user_topic}"))
    markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban {requestor} {user_topic}"))
    await bot.send_message(-1002175092872, f'''
Тема: {user_topic}
Стиль: {style_content}
Ник автора: {requestor}
Приоритет: {TopicPriority}''',reply_markup=markup)
    await bot.reply_to(message, text=default_topic_suggest_message + f'\nВаша позиция в очереди: {await search_number(user_topic,db)}\n Чтобы посмотреть текущую свою позицию в списке,используйте /queue')
    await add_count(requestor)
    await sort_counter()
    last_topic_time[message.chat.id] = time.time()

@bot.message_handler(commands=['banned_themes'])
async def ban_themes(message):
    await bot.send_message(message.chat.id,'''У нас на стриме запрещены темы связанные с:
1)Политикой
2)Детьми
3)Алкоголем,никотиносодержащими изделиями(сигареты и тп),наркотиками(прямым упоминанием веществ)
Пока все,но лишний раз баловаться не нужно''')
async def send_text(message):
    if not(message.chat.id in AdminTgIds):
        await bot.send_message(message.chat.id, "Бро, задай тему с помощью команды /topic, или посмотри подробности с помощью /help")

@bot.message_handler(commands=['queue'])
async def queue(message):
    k = 1
    spisok = ''
    for i in await get_topic_by_user(message.from_user.first_name,db):
        number = await search_number(i,db)
        spisok = spisok + f'{k}) {i} - {number} место в очереди\n'
        k += 1
    await bot.send_message(message.chat.id,spisok)

@bot.callback_query_handler(func=lambda call: True)
async def del_theme(call):
    calldata = call.data.split(' ')
    print(calldata)
    if calldata[0] == 'delete_theme':
        await delete_theme(db,calldata[2])
        await add_warning(calldata[1])
        await bot.reply_to(call.message,'Тема удалена, +1 предупреждение')
    elif calldata[0] == 'ban':
        await block_user(calldata[1])

@bot.message_handler()
async def send_text(message):
    if not(message.chat.id in AdminTgIds):
        await bot.send_message(message.chat.id, "Бро, задай тему с помощью команды /topic, или посмотри подробности с помощью /help")

print('Запуск ТГ бота...')

asyncio.run(bot.polling(skip_pending=True))
