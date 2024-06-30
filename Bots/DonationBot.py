import json
import socketio
import os
from myConfig import valid_speakers, replacements
from dotenv import load_dotenv
from Mongodb.BotsScripts import add_topic,add_mashup,connect_to_mongodb,replace_name

load_dotenv()

# Добавляем путь к каталогу, где находится _myConfig.py
#sys.path.append(r'N:\AI-Stream-Kit\Stream-Kit\Configs')
#import _myConfig

# TOKENDONAT = _myConfig.TOKENDONAT

# Credentials
# mongodb_address = _myConfig.mongodb_address

InteractionOneSumRub = 25
InteractionTwoSumRub = 30
AddTopicSumRub = 50
AddMashupSumRub = 100

# valid_speakers = _myConfig.valid_speakers
# replacements = _myConfig.replacements

# Функция подключения к mongodb

     
db = connect_to_mongodb()  

print(db)

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    sio.emit('add-user', {"token": os.getenv('TOKENDON'), "type": "alert_widget"})

@sio.on('donation')
def on_message(data):
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
    
    
    if (currency == 'RUB'):
        if (FinalAmount == AddMashupSumRub):
            print('Мэшап задоначен')
            
            if not(message.startswith('!мэшап')):
                print('Некорректный запрос мэшапа!')
                print()
                return
                
            mashup = message.split("!мэшап ", 1)[1]
            requestor = f'Донатер {user}'
            
            if mashup and " " in mashup:
                speaker, url = mashup.split(" ", 1)
                if speaker in valid_speakers:
                    eng_speaker = replace_name(speaker, replacements)
                    add_mashup(db, requestor, "Donat", 2, eng_speaker, url)
                else:
                    print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                    print()
            else:
                print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                print()
            
        elif (FinalAmount == AddTopicSumRub):
            print('Тема задоначена')
            if "!стиль" in message:
                style_content = message.split("!стиль ", 1)[1]
                message = message.split("!стиль ", 1)[0].strip()
            else:
                style_content = "Комедийный, поучительный"
            requestor = f'Донатер {user}'
            add_topic(db, requestor, "Donat", 2, message, style_content)  # Добавляем тему в БД
            
        elif FinalAmount == InteractionOneSumRub:
            print('Цветок задоначен')
            data = 'Flower: ' + str(donat['username'])
            addDonationData(data)
        elif FinalAmount == InteractionTwoSumRub:
            print('Танец задоначен')
            addDonationData('Dance')
            
        
def clear_file():
    with open("DonationData.txt", "a", encoding="utf-8") as file:
        file.write('')
        
            
def addDonationData(str):
    with open("DonationData.txt", "a", encoding="utf-8") as file:
        file.write(str + "\n")
        print("Добавлено в файл: ", str)
        print()
        
        
        # Добавление сценария в БД


sio.connect('wss://socket.donationalerts.ru:443',transports='websocket')
clear_file()
