import asyncio
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot, types
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
from myConfig import AdminTgIds, ChanelToSubscribeID, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message,threshold, MaxLengthTG, DonatedTopicSumRub, SubsLvl1ChatID
from Mongodb.CountScripts import warnings_by_user,add_count, sort_counter,add_warning,block_user,search_nick
from Mongodb.BotsScripts import add_topic,connect_to_mongodb,filt,delete_theme,search_number,\
    get_topic_by_user,check_topic_exists, check_topic_style, get_members_id,\
    up_theme, add_interaction, get_parameters_by_topic_id,get_id_by_theme_number
from quart import Quart, request

load_dotenv()
bot = AsyncTeleBot(os.getenv('TOKENTG'))
mode = 'on'
last_topic_time = {}
# Функция подключения к mongodb
db = connect_to_mongodb()
source = 'Telegram'

users_good = 0
users_bad = 0

# Получение запроса от Node JS
app = Quart(__name__)
@app.route('/telegram-webhook', methods=['POST'])
async def telegram_webhook():
    data = await request.json
    text = data.get('text')
    if text: 
        if (id_3 := await get_id_by_theme_number(db, 2)):
            await send_notification(SubsLvl1ChatID, id_3, 3)
        if (id_1 := await get_id_by_theme_number(db, 0)):
            await send_notification(SubsLvl1ChatID, id_1, 1)
        #print(text, notification_id)
        return {'status': 'success'}
    else:
        return {'status': 'failed'}, 400

async def send_notification(chat_id, admin_id, position):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == admin_id:
                if position == 1:
                    text = 'Твоя тема будет прямо сейчас! [(СТРИМ ТУТ)](https://www.tiktok.com/@neurogta/live)'
                else:
                    text = 'Твоя тема скоро будет в эфире! Номер в очереди: 3'
                await bot.send_message(admin_id, text, parse_mode='Markdown')
                return None
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


async def send_message_to_user(user_id, message):
    global users_bad, users_good
    try:
        await bot.send_message(user_id, message)
        print(f"Сообщение отправлено пользователю с ID {user_id}")
        users_good += 1
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю с ID {user_id}: {e}")
        users_bad += 1


@bot.message_handler(commands=['spam'])
async def spam(message):
    if not(message.chat.id in AdminTgIds):
        return
    url = message.text[6:]
    await bot.send_message(message.chat.id, 'Начинаю рассылку с приглашением на стрим!')
    try:
        all_id = await get_members_id(db)
        for user_id in all_id:
            await send_message_to_user(user_id, url)
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка при рассылке: {e}")
    await bot.send_message(message.chat.id, f'Отправлено: {users_good}. Заблокировано: {users_bad}.')

@bot.message_handler(commands=['action'])
async def add_action(message):
    if not(message.chat.id in AdminTgIds):
        return
    action_parameter = message.text[8:].strip()
    if ' ' in action_parameter:
        action, parameter = action_parameter.split(' ', 1)
    else:
        action = action_parameter
        parameter = "" 
    await add_interaction(db, action, parameter)
    await bot.send_message(message.chat.id, f"Действие добавлено в базу")

@bot.message_handler(commands=['skip'])
async def skip(message):
    if not(message.chat.id in AdminTgIds):
        return
    await add_interaction(db, "skip", "")
    await bot.send_message(message.chat.id, f"История скипнута")

@bot.message_handler(commands=['save'])
async def save(message):
    if not(message.chat.id in AdminTgIds):
        return
    await add_interaction(db, "save", "")
    await bot.send_message(message.chat.id, f"История сохранена")

@bot.message_handler(commands=['test'])
async def test(message):
    if not(message.chat.id in AdminTgIds):
        return
    link = "[СТРИМ](https://www.tiktok.com/@neurogta/live)"
    await bot.send_message(AdminTgIds[1], link, parse_mode='Markdown')



@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, 'Wassup, nigga🖐️\n'
                                            'Здесь ты можешь предложить тему на стрим Нейро GTA.\n'
                                            '/topic - Задать тему\n\n'
                                            '/help - Для подробной информации\n'
                                            '/ban_themes - Правила и запрещенные темы\n'
                                            '/queue - Посмотреть свою очередь\n\n'
                                            f'За {DonatedTopicSumRub}₽ можно заказать тему без очереди!\nhttps://www.donationalerts.com/r/neuro_gta')


# Сообщение с информацией
@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, 'Все до жути просто, братан. Просто пиши команду "/topic", а дальше свою тему 😊\n\n'
                                            "Также по желанию можно добавить истории свой стиль (жанр). Для этого нужно после темы добавить команду !стиль [Свой стиль] 🎨\n"
                                            'Пример: "/topic CJ и Smoke осознали что ими управляет нейросеть !стиль хоррор" \n\n'
                                            'Избегай запрещенных тем, описанных в команде /ban_themes \n'
                                            'Такие темы не будут сгенерированы, а если пытаться обойти правила, можно получить бан 🚷\n\n'
                                            'Очередь своих тем можно узнать командой /queue ⏳\n'
                                            'Эта команда выведет все твои темы, которые находятся в очереди, и их порядковый номер 📋\n\n'
                                            "P.S. В нашем дискорд сервере задержка на добавление темы меньше ⏱️. Секретная ссылка на наш дискорд: https://discord.gg/HcfJw5umC3\n\n"
                                            "P.S.S Заказать тему без очереди (и просто оказать поддержку) можно здесь:\n"
                                            'https://www.donationalerts.com/r/neuro_gta 💖')


# Передача тем от бота
@bot.message_handler(commands=['topic'])
async def topic(message):
    try:
        chat_member = await bot.get_chat_member(ChanelToSubscribeID, message.from_user.id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            await bot.send_message(message.chat.id, "Пожалуйста, подпишитесь на наш канал, чтобы задавать темы\n"
                                                    f"https://t.me/{ChanelToSubscribeID[1:]}")
            return
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


    topic = message.text[7:]
    requestor_name = message.from_user.first_name
    requestor_id = message.from_user.id
    user_tag = f'@{message.from_user.username}'
    warnings = await warnings_by_user(requestor_name, source, requestor_id)
    if mode == 'off':
        await bot.send_message(message.chat.id,'Сожалеем,но прием тем на этом стриме уже завершен, ждем ваши темы на следующем.\n    - с любовью,Meyson\n\nPs. Темы все еще можно задавать за донат(без очереди) https://www.donationalerts.com/r/neuro_gta')
        await bot.send_sticker(message.chat.id,'CAACAgIAAxkBAAEMZ-JmgY_WuGvpBWdSmJ99nMQgy7qMqQACBxkAAs0xEEghvxdEJ73qJDUE')
        return
    if warnings == 5:
        await block_user(requestor_name,requestor_id,user_tag,requestor_id)
    if await search_nick(requestor_name,'BlackList',source,requestor_id):
        await bot.send_message(message.chat.id,'Сожалеем,но вы заблокированы за нарушение правил. Вы можете попробовать вымолить прощение у @Meyson420')
        return
    if topic == '' or topic == 'NeuroGta_bot':
        await bot.send_message(message.chat.id, 'Тема не может быть пустой. Пожалуйста, напиши свою тему сразу после команды /topic')
        return
    if await filt(topic):
        await add_warning(requestor_name,source,requestor_id)
        last_topic_time[requestor_id] = time.time()
        if warnings is None:
            warnings = 0
        await bot.send_message(message.chat.id, 'Ай-ай-ай,у нас тут так не принято. Не нужно кидать запрещенные темы\n/ban_themes - Запрещенные темы')
        await bot.send_message(message.chat.id,f'На данный момент у вас {warnings+1} предупреждений.')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban|&|{requestor_id}"))
        await bot.send_message(-1002175092872, f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Тег: {user_tag}
Источник: {source}
Количество предупреждений: {warnings+1}''',reply_markup=markup)
        return

    topic, style_content = await check_topic_style(topic)

    check_result = await check_topic_exists(db, topic, threshold)
    if len(topic) > MaxLengthTG:
        if not(message.chat.id in AdminTgIds):
            await bot.send_message(message.chat.id,f'Тема слишком большая.\nТема должна быть не больше {MaxLengthTG} символов')
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban|&|{requestor_id}"))
            await bot.send_message(-1002175092872, f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Тег: {user_tag}
Источник: {source}
Длина темы: {len(topic)}''',reply_markup=markup)
            return
    if check_result[0]:
         procent, orig = check_result[1],check_result[2]
         await bot.send_message(message.chat.id, 'Тема не добавлена!\nТакая тема(или подобная ей) уже есть в очереди.\nПридумайте что-нибудь другое')
         await bot.send_message(-1002175092872, f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Тег: {user_tag}
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


    topic_id = await add_topic(db, requestor_name, user_tag, requestor_id, source, TopicPriority, topic, style_content)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🗑 Удалить тему', callback_data=f"del|&|{requestor_id}|&|{topic_id}"))
    markup.add(InlineKeyboardButton('🗑 Удалить тему + Предупреждение', callback_data=f"delpred|&|{requestor_id}|&|{topic_id}"))
    markup.add(InlineKeyboardButton('🖕 Заблокировать', callback_data= f"ban|&|{requestor_id}|&|{topic_id}"))
    markup.add(InlineKeyboardButton('⬆️ Повысить приоритет',callback_data= f'up|&|{requestor_id}|&|{topic_id}'))
    await bot.send_message(-1002175092872, f'''
Тема: {topic}
Стиль: {style_content}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Тег: {user_tag}
Источник: {source}
Приоритет: {TopicPriority}''',reply_markup=markup)
    markup2 = InlineKeyboardMarkup()
    markup2.add(InlineKeyboardButton('⬆️ Отправить тему без очереди',callback_data= f'up|&|{requestor_id}|&|{topic_id}'))
    markup2.add(InlineKeyboardButton('🔊 Включить уведомление',callback_data= f'notice|&|{requestor_id}|&|{topic_id}'))
    await bot.reply_to(message, text=default_topic_suggest_message + f'\nТвоя позиция в очереди: {await search_number(topic_id,db)}\n\nЧтобы посмотреть свою текущую позицию в очереди, используй команду:\n/queue',reply_markup = markup2)
    await add_count(requestor_name, source, str(requestor_id))
    await sort_counter()
    await bot.send_message(message.chat.id,'Хочешь получить уведомление,когда придет время твоей темы? \n➡️️ Пиши /subscribe')
    last_topic_time[requestor_id] = time.time()

@bot.message_handler(commands=['ban_themes'])
async def ban_themes(message):
    await bot.send_message(message.chat.id,'''🚫У нас на стриме запрещены темы, в которых обсуждается:
1)Политика
2)Дети
3)Религия
4)Алкоголь, никотиносодержащие изделия (сигареты и тп), наркотики (прямое упоминанием веществ)
5)Аморальщина
                           
Если вы отправили запрещенную тему, вы получите предупреждение автоматически.
При попытке обхода правил модераторы также могут отклонить вашу тему и выдать предупреждение.
                            
Соблюдайте правила, и радуйтесь своим темам на стриме 💖''')

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
    if spisok == '':
        spisok = 'Пока у тебя нет тем в очереди.'
    await bot.send_message(message.chat.id,f'{spisok}\n\nP.S. Если до твоей темы далеко - за {DonatedTopicSumRub}₽ можно заказать тему без очереди!\nhttps://www.donationalerts.com/r/neuro_gta 💖')
    #await bot.send_message(message.chat.id,spisok)
@bot.message_handler(commands=['subscribe'])
async def subscribe(message):
    await bot.send_message(message.chat.id,'Услуга пока недоступна')
@bot.callback_query_handler(func=lambda call: True)
async def del_theme(call):
    calldata = call.data.split('|&|')
    but = calldata[0]
    user_id = calldata[1]
    topic_id = calldata[2]
    topic, user_name, user_tag, source = await get_parameters_by_topic_id(db, topic_id, 'topic', 'requestor_name', 'user_tag', 'source')
    print(user_name, user_tag, source)
    if but == 'del':
        await delete_theme(db,topic_id)
        await bot.reply_to(call.message,'Тема удалена')
        await bot.send_message(user_id, f'Ваша тема "{topic}" была удалена модераторами.')
    elif but == 'delpred':
        await delete_theme(db,topic_id)
        await add_warning(user_name,source,user_id)
        warns = await warnings_by_user(user_name, source, user_id)
        await bot.reply_to(call.message,'Тема удалена, +1 предупреждение')
        await bot.send_message(user_id, f'Ваша тема "{topic}" была удалена модераторами.\nКоличество предупреждений: {warns}/5')
    elif but == 'ban':
        await block_user(source,user_name,user_tag,user_id)
        await bot.reply_to(call.message,'Пользователь заблокирован. Ебать он лох')
        await bot.send_message(user_id, 'Поздравляем, вы были заблокированы за нарушение правил! :)')
    elif but == 'up':
        await up_theme(db,topic_id)
        await bot.reply_to(call.message,'Приоритет темы повышен.')
    elif but == 'notice':
        pass

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
            await bot.send_message(message.chat.id,'Сожалеем,но прием тем на этом стриме уже завершен, ждем ваши темы на следующем.\n    - с любовью,Meyson\n\nPs. Темы все еще можно задавать за донат(без очереди) https://www.donationalerts.com/r/neuro_gta')
            await bot.send_sticker(message.chat.id,'CAACAgIAAxkBAAEMZ-JmgY_WuGvpBWdSmJ99nMQgy7qMqQACBxkAAs0xEEghvxdEJ73qJDUE')


print('Запуск ТГ бота...')



async def main():
    # Запуск сервера Quart
    await asyncio.gather(
        app.run_task(port=3000),  # Запуск сервера Quart в фоновом режиме
        bot.polling(non_stop=True, skip_pending=True)  # Запуск бота
    )

if __name__ == '__main__':
    asyncio.run(main())


