import asyncio
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot, types
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
from Bots.TelegramTexts import start_sms, subs_sms, help_sms, cover_sms, intro_sms, rules_sms, donate_sms
from myConfig import AdminTgIds, ChanelToSubscribeID, NeedTopicDelay, TopicDelayTg, TopicPriority, \
    default_topic_suggest_message,threshold, MaxLengthTG, DonatedTopicSumRub, SubsChatsIDs, DonateUrl, \
    SubsUpTopicCount, SubsUpTopicDelay, UrlPlatinum, UrlLegendary, valid_speakers, replacements
from Mongodb.CountScripts import warnings_by_user,add_count, sort_counter,add_warning,block_user,search_nick
from Mongodb.BotsScripts import add_topic,connect_to_mongodb,filt,delete_theme,search_number,\
    get_topic_by_user,check_topic_exists, check_topic_style, get_members_id, edit_topic,\
    up_theme, add_interaction, get_parameters_by_topic_id,get_id_by_theme_number, add_mashup, replace_name
from quart import Quart, request

load_dotenv()
bot = AsyncTeleBot(os.getenv('TOKENTG'))
mode = 'on'
last_topic_time = {}
subs_data = {}
# Функция подключения к mongodb
db = connect_to_mongodb()
source = 'Telegram'

users_good = 0
users_bad = 0

user_responses = {}
last_id = ''

#region Сервер вебхуков
app = Quart(__name__)
@app.route('/telegram-webhook', methods=['POST'])
async def telegram_webhook():
    data = await request.json
    action = data.get('action')
    match action:
        case "CheckQueue":
            if (id_3 := await get_id_by_theme_number(db, 2)):
                if await check_for_admin(SubsChatsIDs[0], id_3) or await check_for_admin(SubsChatsIDs[1], id_3): 
                    await send_notification(id_3, 3)
            if (id_1 := await get_id_by_theme_number(db, 0)):
                if await check_for_admin(SubsChatsIDs[0], id_1) or await check_for_admin(SubsChatsIDs[1], id_1):
                    await send_notification(id_1, 1)
            #print(text, notification_id)
            return {'status': 'success'}
        case "MashupError":
            await bot.send_message(AdminTgIds[1], "❗️ОШИБКА ПРИ СОЗДАНИИ МЭШАПА❗️")
            return {'status': 'success'}
        case "TopicError":
            await bot.send_message(AdminTgIds[1], "❗️ОШИБКА ПРИ СОЗДАНИИ ТЕМЫ❗️")
            return {'status': 'success'}
        case "Waiting":
            text = data.get('text')
            full_text = "\n\n".join(f"{line['character']}: {line['dialogue']}" for line in text)
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
            InlineKeyboardButton("Заебись👍", callback_data='good'),
            InlineKeyboardButton("Хуево👎", callback_data='bad'))
            keyboard.add(InlineKeyboardButton("Изменить тему/стиль🔄", callback_data='edit'))

            message = await bot.send_message(AdminTgIds[2], full_text, reply_markup=keyboard)
            user_responses[message.message_id] = None
            while user_responses[message.message_id] not in ["good", "bad"]:
                await asyncio.sleep(1)
            if user_responses[message.message_id] == 'good':
                return {'status': 'success'}
            else:
                return {'status': 'failed'}, 400
            
    return {'status': 'failed'}, 400
#endregion

#region Доп Функции
async def check_for_admin(chat_id, admin_id):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if str(admin.user.id) == str(admin_id):
                return True
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False
    
async def check_for_sub(id):
    chat_member = await bot.get_chat_member(ChanelToSubscribeID, id)
    return chat_member.status in ['member', 'administrator', 'creator']

async def send_notification(admin_id, position):
    try:
        if position == 1:
            text = '🔔Твоя тема будет прямо сейчас! [(СТРИМ ТУТ)](https://www.tiktok.com/@neurogta/live)'
        else:
            text = '⏰Твоя тема скоро будет в эфире! Номер в очереди: 3'
        await bot.send_message(admin_id, text, parse_mode='Markdown')
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

#endregion

#region Общие команды

@bot.message_handler(commands=['start'])
async def start(message):
    if await check_for_sub(message.from_user.id) == False:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="✅Я подписался", callback_data=f"sub|&|{message.from_user.id}"))
            await bot.send_message(message.chat.id, "Привет, бро! \n\n"
                                   "Добро пожаловать в официальный бот проекта Нейро GTA! \n\n"
                                   "Для того чтобы воспользоваться ботом, тебе необходимо быть подписчиком нашего Telegram-канала\n"
                                                    f"Нейро GTA {ChanelToSubscribeID}", reply_markup=keyboard)
            return
    await bot.send_message(message.chat.id, start_sms)

@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, help_sms)

@bot.message_handler(commands=['topic'])
async def topic(message):
    try:
        if await check_for_sub(message.from_user.id) == False:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="✅Я подписался", callback_data=f"sub|&|{message.from_user.id}"))
            await bot.send_message(message.chat.id, "Для того, чтобы отправлять темы для генерации сценариев на стрим, тебе необходимо быть подписчиком нашего Telegram-канала\n"
                                                    f"Нейро GTA {ChanelToSubscribeID}", reply_markup=keyboard)
            return
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


    topic = message.text[7:]
    requestor_name = message.from_user.first_name
    requestor_id = message.from_user.id
    user_tag = f'@{message.from_user.username}'
    warnings = await warnings_by_user(requestor_name, source, requestor_id)
    if mode == 'off':
        if not (await check_for_admin(SubsChatsIDs[0], requestor_id) or await check_for_admin(SubsChatsIDs[1], requestor_id)):
            await send_off_mode_text(message)
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
        await bot.send_message(message.chat.id, 'Ай-ай-ай,у нас тут так не принято. Не нужно кидать запрещенные темы\n/rules - Запрещенные темы')
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
    markup2.add(InlineKeyboardButton('🚀 Отправить тему без очереди',callback_data= f'up-user|&|{requestor_id}|&|{topic_id}'))
    markup2.add(InlineKeyboardButton('🔔 Уведомление о начале темы',callback_data= f'notice|&|{requestor_id}|&|{topic_id}'))
    await bot.reply_to(message, text=default_topic_suggest_message + f'\nТвоя позиция в очереди: {await search_number(topic_id,db)}\n\nЧтобы посмотреть свою текущую позицию в очереди, используй команду:\n/queue',reply_markup = markup2)
    await add_count(requestor_name, source, str(requestor_id))
    await sort_counter()
    #await bot.send_message(message.chat.id,'Хочешь получить уведомление,когда придет время твоей темы? \n➡️️ Пиши /subscribe')
    last_topic_time[requestor_id] = time.time()

@bot.message_handler(commands=['rules'])
async def rules(message):
    await bot.send_message(message.chat.id, rules_sms)

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
    await bot.send_message(message.chat.id,f'{spisok}\n\nP.S. Если до твоей темы далеко - за {DonatedTopicSumRub}₽ можно заказать тему без очереди!\n{DonateUrl} 💖\n\nP.P.S А чтобы получать уведомления о начале своей темы и запускать темы без очереди прямо в телеграме - напиши /subscribe 😍')
    #await bot.send_message(message.chat.id,spisok)

@bot.message_handler(commands=['subscribe'])
async def subscribe(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="💎PLATINUM💎", url=UrlPlatinum))
    markup.add(InlineKeyboardButton(text="👑LEGENDARY👑", url=UrlLegendary))
    #await bot.send_message(message.chat.id, "Выберите желаемый уровень подписки", reply_markup=markup)
    await bot.send_message(message.chat.id, subs_sms, parse_mode="Markdown", reply_markup=markup)
                       
@bot.callback_query_handler(func=lambda call: True)
async def callbacks(call):
    if call.data in ["good", "bad", "edit"]:
        user_responses[call.message.message_id] = call.data
        match call.data:
            case 'bad':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            case 'good':
                await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            case 'edit':
                await bot.send_message(call.message.chat.id, "Напиши новую тему и/или стиль")
                global mode, last_id
                mode = 'edit'
                last_id = call.message.message_id
        return
                
    calldata = call.data.split('|&|')
    but = calldata[0]
    user_id = calldata[1]

    if but == "sub":
        if await check_for_sub(user_id) == False:
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton(text="✅Теперь точно подписался", callback_data=f"sub|&|{user_id}"))
                    await bot.send_message(user_id, "Ошибка, ты не являешься подписчиком Telegram-канала\n"
                                                    f"Нейро GTA {ChanelToSubscribeID}", reply_markup=keyboard)
        else:
            await bot.send_message(user_id, intro_sms, parse_mode='Markdown')
        return
    
    elif but == 'ban':
        chat_info = await bot.get_chat(user_id)
        user_tag = f'@{chat_info.username}' 
        user_name = chat_info.first_name
        global source
        await block_user(source,user_name,user_tag,user_id)
        await bot.reply_to(call.message,'Пользователь заблокирован. Ебать он лох')
        await bot.send_message(user_id, 'Поздравляем, вы были заблокированы за нарушение правил! :)')
        return

    topic_id = calldata[2]
    topic, user_name, user_tag, source = await get_parameters_by_topic_id(db, topic_id, 'topic', 'requestor_name', 'user_tag', 'source')
    print(user_name, user_tag, source)
    if but == 'del':
        await delete_theme(db,topic_id)
        await bot.reply_to(call.message,'Тема удалена')
        await bot.send_message(user_id, f'Ваша тема "{topic}" была удалена модераторами.')
    elif but == 'delpred':
        try:
            await delete_theme(db,topic_id)
        except:
            await bot.reply_to(call.message,'Ошибка при удалении темы')
        await add_warning(user_name,source,user_id)
        warns = await warnings_by_user(user_name, source, user_id)
        await bot.reply_to(call.message,'Тема удалена, +1 предупреждение')
        await bot.send_message(user_id, f'Ваша тема "{topic}" была удалена модераторами.\nКоличество предупреждений: {warns}/5')
    elif but == 'up':
        await up_theme(db,topic_id)
        await bot.reply_to(call.message,'Приоритет темы повышен.')
    elif but == 'up-user':
        if await check_for_admin(SubsChatsIDs[1], user_id):
            if user_id in subs_data:
                if time.time() - subs_data[user_id]['last_time'] < SubsUpTopicDelay:
                    await bot.send_message(user_id, f'⏰Отправлять тему без очереди можно раз в {int(SubsUpTopicDelay/60)} минут.')
                elif subs_data[user_id]['count'] >= SubsUpTopicCount:
                    await bot.send_message(user_id, f'😔Лимит тем без очереди на этом стриме исчерпан. Каждый стрим вы можете отправить столько тем без очереди: {SubsUpTopicCount}')
                else:
                    subs_data[user_id]['count']+=1
                    subs_data[user_id]['last_time'] = time.time()
                    await up_theme(db,topic_id)
                    await bot.send_message(user_id, f'🚀Тема отправлена без очереди!')
            else:
                subs_data[user_id] = {'last_time': time.time(), 'count': 1}
                await up_theme(db,topic_id)
                await bot.send_message(user_id, f'🚀Тема отправлена без очереди!')
        else:
            await bot.send_message(user_id, '🔒Данная функция доступна только подписчикам уровня *"LEGENDARY"*\nОформить подписку: /subscribe', parse_mode="Markdown")
        pass
    elif but == 'notice':
        if await check_for_admin(SubsChatsIDs[1], user_id) or await check_for_admin(SubsChatsIDs[0], user_id):
            await bot.send_message(user_id, f'✅Вы уже являетесь подписчиком. Уведомления включены')
        else:
           await bot.send_message(user_id, '🔒Данная функция доступна только подписчикам уровня *"PLATINUM"* и *"LEGENDARY"*\nОформить подписку: /subscribe', parse_mode="Markdown") 
        pass


@bot.message_handler(commands=['donate'])
async def donate(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="❤️Поддержать проект❤️", url=f"{DonateUrl}"))
    await bot.send_message(message.chat.id, donate_sms, parse_mode='Markdown', reply_markup=keyboard)
    
@bot.message_handler(commands=['cover'])
async def cover(message):
     await bot.send_message(message.chat.id, cover_sms, parse_mode='Markdown')

#endregion


#region Админ команды
@bot.message_handler(commands=['spam'])
async def spam(message):
    if not(message.chat.id in AdminTgIds):
        return
    text = message.text[6:]
    await bot.send_message(message.chat.id, 'Начинаю рассылку с приглашением на стрим!')
    try:
        all_id = await get_members_id(db)
        for user_id in all_id:
            await send_message_to_user(user_id, text)
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка при рассылке: {e}")
    await bot.send_message(message.chat.id, f'Отправлено: {users_good}. Заблокировано: {users_bad}.')

@bot.message_handler(commands=['spam_forwarded'])
async def spam(message):
    if not(message.chat.id in AdminTgIds):
        return
    global mode
    mode = "spam"
    await bot.send_message(message.chat.id, "❗️Внимание, следющее сообщение будет отправлено всем подписчикам!❗️")

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

@bot.message_handler(commands='off')
async def off(message):
    if not(message.chat.id in AdminTgIds):
        return
    global mode
    mode = 'off'
    await bot.send_message(message.chat.id, "Приём тем закрыт")

@bot.message_handler(commands='on')
async def on(message):
    if not(message.chat.id in AdminTgIds):
        return
    global mode
    mode = 'on'
    await bot.send_message(message.chat.id, "Приём тем открыт")

@bot.message_handler(commands='delay')
async def delay(message):
    global TopicDelayTg
    if not(message.chat.id in AdminTgIds):
        return
    if message.text[7:] == "":
        await bot.send_message(message.chat.id, f"Текущее кд: {TopicDelayTg} секунд. ({TopicDelayTg/60} минут)") 
    else:
        TopicDelayTg = int(message.text[7:])
        await bot.send_message(message.chat.id, f"Новое кд: {TopicDelayTg} секунд. ({TopicDelayTg/60} минут)")   

@bot.message_handler(commands='edit')
async def edit(message):
    if not(message.chat.id in AdminTgIds):
        return
    await try_edit_topic(message.chat.id, message.text[6:])

@bot.message_handler(commands='meyson')
async def meyson(message):

    mashup = message.text.split("/meyson ", 1)[1]
    requestor = message.from_user.first_name

    if mashup and " " in mashup:
        speaker, url = mashup.split(" ", 1)
        if speaker.upper() in valid_speakers:
            eng_speaker = replace_name(speaker, replacements)
            await add_mashup(db, requestor, message.from_user.id, source, 1, eng_speaker, url)
            await bot.send_message(message.chat.id, "Добавили кавер")

#endregion    
  
@bot.message_handler(content_types=['text', 'photo', 'sticker', 'document', 'audio', 'video', 'voice'])
async def send_text(message):
    global mode, last_id
    
    if message.chat.id in AdminTgIds:
        if mode == 'edit':
            await try_edit_topic(message.chat.id, message.text)
            user_responses[last_id] = "bad"
            mode = "on"
        if mode == 'spam':
            mode = 'on'
            try:
                all_id = await get_members_id(db)
                for user_id in all_id:
                    try:
                        await bot.copy_message(user_id, message.chat.id, message.id)
                        print(f'Отправлено юзеру {user_id}')
                    except Exception as e:
                        print(f"Ошибка при отправке юзеру {user_id} {e}")
            except Exception as e:
                await bot.send_message(message.chat.id, f"Произошла ошибка при рассылке: {e}")
    
    if not(message.chat.id in AdminTgIds) and not(message.chat.id in SubsChatsIDs):
        if mode == 'on':
           await bot.send_message(message.chat.id, "Бро, задай тему с помощью команды /topic, или посмотри подробности с помощью /help")
        if mode == 'off':
            user_id = message.from_user.id
            if not (await check_for_admin(SubsChatsIDs[0], user_id) or await check_for_admin(SubsChatsIDs[1], user_id)):
                await send_off_mode_text(message)
            else:
                 await bot.send_message(message.chat.id, "Круто, ты СуперПодписчик, можешь задавать тему, когда никто уже не может!😎\nЖду команду /topic")
        
async def try_edit_topic(chat_id, message):
    if await edit_topic(db, message):
        await bot.send_message(chat_id, "Изменения применены")
    else:
        await bot.send_message(chat_id, "Не удалось применить изменения")

async def send_off_mode_text(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Поддержать проект", url=f"{DonateUrl}"))
    keyboard.add(InlineKeyboardButton(text="Подписаться", url=UrlPlatinum))
    await bot.send_message(message.chat.id,f'''Сожалеем, но приём тем на текущий стрим приостановлен, ждем ваши темы на следующем стриме.
             - с любовью,Meyson

🤩 Темы все еще можно задавать за донат(без очереди) [здесь]({DonateUrl})
❤️Либо оформив подписку /subscribe''', parse_mode='Markdown', reply_markup=keyboard)
    await bot.send_sticker(message.chat.id,'CAACAgIAAxkBAAEMZ-JmgY_WuGvpBWdSmJ99nMQgy7qMqQACBxkAAs0xEEghvxdEJ73qJDUE')



print('Запуск ТГ бота...')

async def main():
    # Запуск сервера Quart
    await asyncio.gather(
        app.run_task(port=4000),  # Запуск сервера Quart в фоновом режиме
        bot.polling(non_stop=True, skip_pending=True)  # Запуск бота
    )

if __name__ == '__main__':
    asyncio.run(main())
