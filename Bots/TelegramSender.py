import requests
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

TG_API_TOKEN = os.getenv('TOKENTG')
TELEGRAM_CHAT_ID = -1002175092872
TG_API_URL = f'https://api.telegram.org/bot{TG_API_TOKEN}/sendMessage'


async def send_topic_to_telegram(topic, style, requestor_name, requestor_id, source, prioritet, topic_id):
    message = f'''
Тема: {topic}
Стиль: {style}
Ник автора: {requestor_name}
Айди пользователя: {requestor_id}
Источник: {source}
Приоритет: {prioritet}'''
    print(message)

    inline_keyboard = [
        [{"text": "🗑 Удалить тему", "callback_data": f"del|&|{requestor_id}|&|{topic_id}"}],
        [{"text": "🖕 Заблокировать", "callback_data": f"ban|&|{requestor_id}|&|{topic_id}"}]
    ]
    reply_markup = {"inline_keyboard": inline_keyboard}

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
    }

    try:
        response = requests.post(TG_API_URL, data=payload)
        if response.status_code == 200:
            print(f'Тема отправлена в телеграм на модерацию')
        else:
            print(f'Ошибка отправки в телеграм: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Ошибка отправки в телеграм: {e}')