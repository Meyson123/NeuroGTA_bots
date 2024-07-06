import json
import socketio
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from myConfig import Project, valid_speakers, replacements, DonatEnableInteractionOne, DonatEnableInteractionTwo, \
    DonatEnableTopics, DonatEnableMashups, DonatedInteractionOneSumRub, DonatedInteractionTwoSumRub, \
    DonatedMashupSumRub, DonatedTopicSumRub
from dotenv import load_dotenv
from Mongodb.BotsScripts import add_topic, add_mashup, connect_to_mongodb, replace_name, filter,check_topic_style
from TelegramSender import send_donated, send_filter_error, send_topic_to_telegram

load_dotenv()
db = connect_to_mongodb()
print(db)
donated_id = 0
source = 'Donation'

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    try:
        if Project == 'Gta':
            token = os.getenv('TOKENDONATGTA')
        else:
            token = os.getenv('TOKENDONATSMESH')
        sio.emit('add-user', {"token": token, "type": "alert_widget"})
        print("Connected to the server")
    except Exception as e:
        print(f"Error during connection: {e}")

@sio.on('disconnect')
def on_disconnect():
    print("Disconnected from server")

@sio.on('donation')
def on_message(data):
    try:
        donat = json.loads(data)
        user = donat['username']
        amount = donat['amount']
        message = donat['message']
        currency = donat['currency']

        if user is None:
            user = "Аноним"

        donation_info = f'''
{user} задонатил {amount} {currency}
Сообщение: {message}'''

        asyncio.run(send_donated(donation_info))
        print(f"Received donation: {donation_info}")

        global donated_id
        donated_id += 1
        requestor_id = str(donated_id).zfill(4)

        FinalAmount = 0
        if isinstance(amount, int):
            FinalAmount = amount
        elif isinstance(amount, float):
            FinalAmount = int(amount)
        elif isinstance(amount, str):
            amountSplit = amount.split('.')
            FinalAmount = int(amountSplit[0])

        if currency == 'RUB':
            if FinalAmount >= DonatedMashupSumRub and DonatEnableMashups:
                print('Мэшап задоначен')

                if not message.startswith('!мэшап'):
                    print('Некорректный запрос мэшапа!')
                    return

                mashup = message.split("!мэшап ", 1)[1]
                requestor = f'Донатер {user}'

                if mashup and " " in mashup:
                    speaker, url = mashup.split(" ", 1)
                    if speaker in valid_speakers:
                        eng_speaker = replace_name(speaker, replacements)
                        asyncio.run(add_mashup(db, requestor, source, 2, eng_speaker, url))
                    else:
                        print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                else:
                    print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")

            elif FinalAmount >= DonatedTopicSumRub and DonatEnableTopics:
                print('Тема задоначена')
                requestor_name = f'Донатер {user}'

                if asyncio.run(filter(message)):
                    asyncio.run(send_filter_error(message, requestor_name, requestor_id, source, 0, False))
                    return
                
                message, style_content = asyncio.run(check_topic_style(message))

                topic_id = asyncio.run(add_topic(db, requestor_name, requestor_id, source, 2, message, style_content))
                asyncio.run(send_topic_to_telegram(message, style_content, requestor_name, requestor_id, source, 2, str(topic_id), False))

            elif FinalAmount == DonatedInteractionOneSumRub and DonatEnableInteractionOne:
                print('Цветок задоначен')
                data = 'Flower: ' + str(donat['username'])
                add_donation_data(data)

            elif FinalAmount == DonatedInteractionTwoSumRub and DonatEnableInteractionTwo:
                print('Танец задоначен')
                add_donation_data('Dance')
    except Exception as e:
        print(f"Error handling message: {e}")

def clear_file():
    try:
        with open("DonationData.txt", "w", encoding="utf-8") as file:
            file.write('')
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

def add_donation_data(data):
    try:
        with open("DonationData.txt", "a", encoding="utf-8") as file:
            file.write(data + "\n")
            print("Добавлено в файл: " + data)
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

sio.connect('wss://socket.donationalerts.ru:443',transports='websocket')
clear_file()
