import json
import socketio
import os
import sys
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from myConfig import Project, valid_speakers, replacements, DonatEnableInteractionOne, DonatEnableInteractionTwo, \
    DonatEnableTopics, DonatEnableMashups, DonatedInteractionOneSumRub, DonatedInteractionTwoSumRub, \
    DonatedMashupSumRub, DonatedTopicSumRub
from dotenv import load_dotenv
from Mongodb.BotsScripts import add_topic, add_mashup, connect_to_mongodb, replace_name

load_dotenv()

db = connect_to_mongodb()
print(db)

sio = socketio.AsyncClient()

@sio.event
async def connect():
    if Project == 'Gta':
        token = (os.getenv('TOKENDONATGTA'))
    else:
        token = (os.getenv('TOKENDONATSMESH'))
    await sio.emit('add-user', {"token": token, "type": "alert_widget"})

@sio.on('donation')
async def on_message(data):
    donat = json.loads(data)
    
    user = donat['username']
    amount = donat['amount']
    message = donat['message']
    currency = donat['currency']
    
    print(user, 'задонатил', amount, currency)
    print('Сообщение: ', message)
    
    FinalAmount = 0
    if type(amount) == int:
        FinalAmount = amount
    elif type(amount) == float:
        FinalAmount = int(amount)
    elif type(amount) == str:
        amountSplit = amount.split('.')
        FinalAmount = int(amountSplit[0])
    
    if currency == 'RUB':
        if FinalAmount == DonatedMashupSumRub and DonatEnableMashups:
            print('Мэшап задоначен')
            
            if not message.startswith('!мэшап'):
                print('Некорректный запрос мэшапа!')
                print()
                return
                
            mashup = message.split("!мэшап ", 1)[1]
            requestor = f'Донатер {user}'
            
            if mashup and " " in mashup:
                speaker, url = mashup.split(" ", 1)
                if speaker in valid_speakers:
                    eng_speaker = replace_name(speaker, replacements)
                    await add_mashup(db, requestor, "Donat", 2, eng_speaker, url)
                else:
                    print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                    print()
            else:
                print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                print()
            
        elif FinalAmount == DonatedTopicSumRub and DonatEnableTopics:
            print('Тема задоначена')
            if "!стиль" in message:
                style_content = message.split("!стиль ", 1)[1]
                message = message.split("!стиль ", 1)[0].strip()
            else:
                style_content = "Комедийный, поучительный"
            requestor = f'Донатер {user}'
            await add_topic(db, requestor, "Donat", 2, message, style_content)  # Добавляем тему в БД
            
        elif FinalAmount == DonatedInteractionOneSumRub and DonatEnableInteractionOne:
            print('Цветок задоначен')
            data = 'Flower: ' + str(donat['username'])
            await add_donation_data(data)
            
        elif FinalAmount == DonatedInteractionTwoSumRub and DonatEnableInteractionTwo:
            print('Танец задоначен')
            await add_donation_data('Dance')
        
async def clear_file():
    try:
        with open("DonationData.txt", "w", encoding="utf-8") as file:
            file.write('')
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

async def add_donation_data(data):
    try:
        with open("DonationData.txt", "a", encoding="utf-8") as file:
            file.write(data + "\n")
            print("Добавлено в файл: ", data)
            print()
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

async def main():
    await sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
    await clear_file()
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
