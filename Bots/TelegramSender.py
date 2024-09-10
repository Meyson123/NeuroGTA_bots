import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

TG_API_TOKEN = os.getenv('TOKENTG')
TELEGRAM_CHAT_ID = 709479935
TG_API_URL = f'https://api.telegram.org/bot{TG_API_TOKEN}/sendMessage'

async def sending_to_tg(payload=None, text=None):
    if payload == None:
        payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
    }
    try:
        response = requests.post(TG_API_URL, data=payload)
        if response.status_code == 200:
            print(f'Telegram sender: информация отправлена')
        else:
            print(f'Ошибка отправки в телеграм: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Ошибка отправки в телеграм: {e}')


async def send_topic_to_telegram(topic, style, requestor_name, requestor_id, source, priority, topic_id, can_ban_user):
    message = f'''
Тема: {topic}
Стиль: {style}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Приоритет: {priority}'''

    if can_ban_user:
        inline_keyboard = [
            [{"text": "🗑 Удалить тему", "callback_data": f"del|&|{requestor_id}|&|{topic_id}"}],
            [{"text": "🗑 Удалить тему + Предупреждение", "callback_data": f"delpred|&|{requestor_id}|&|{topic_id}"}],
            [{"text": "🖕 Заблокировать", "callback_data": f"ban|&|{requestor_id}|&|{topic_id}"}],
            [{'text': '⬆️ Повысить приоритет',"callback_data": f'up|&|{requestor_id}|&|{topic_id}'}]
        ]
    else:
        inline_keyboard = [
            [{"text": "🗑 Удалить тему", "callback_data": f"del|&|{requestor_id}|&|{topic_id}"}],
        ]
    reply_markup = {"inline_keyboard": inline_keyboard}

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
    }
    await sending_to_tg(payload)


async def send_similar_error(topic,requestor_name,requestor_id,source,orig,procent):
    message = f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Оригинальная тема: {orig}
Процент сходства: {procent}%'''
    inline_keyboard = [
        [{"text": "🖕 Заблокировать", "callback_data": f"ban|&|{requestor_id}"}]
    ]
    reply_markup = {"inline_keyboard": inline_keyboard}

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
    }
    await sending_to_tg(payload)


async def send_filter_error(topic,requestor_name,requestor_id,source,warnings, can_ban_user):
    message =  f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Количество предупреждений: {warnings}'''
    inline_keyboard = [
     [{"text": "🖕 Заблокировать", "callback_data": f"ban|&|{requestor_id}"}]
    ]
    reply_markup = {"inline_keyboard": inline_keyboard}

    if can_ban_user:
        payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
        }
    else:
        payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        }
    await sending_to_tg(payload)

async def send_len_error(topic,requestor_name,requestor_id,source, can_ban_user):
    message = f'''
Тема заблокирована

Тема: {topic}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Длина темы: {len(topic)}'''
    inline_keyboard = [
     [{"text": "🖕 Заблокировать", "callback_data": f"ban|&|{requestor_id}"}]
    ]
    reply_markup = {"inline_keyboard": inline_keyboard}
    if can_ban_user:
        payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
        }
    else:
        payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        }
    await sending_to_tg(payload)
async def send_donated(info):
    message =  f'''
🤑🤑🤑ДОНАТ🤑🤑🤑
{info}
'''

    payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': message,
    }
    await sending_to_tg(payload)
