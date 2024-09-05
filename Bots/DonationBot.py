import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from myConfig import Project, valid_speakers, replacements, DonatEnableInteractionOne, DonatEnableInteractionTwo, \
    DonatEnableTopics, DonatEnableMashups, DonatedInteractionOneSumRub, DonatedInteractionTwoSumRub, \
    DonatedMashupSumRub, DonatedTopicSumRub
from dotenv import load_dotenv
from Mongodb.BotsScripts import add_topic, add_mashup, connect_to_mongodb, replace_name, filt,check_topic_style, add_interaction
from TelegramSender import send_donated, send_filter_error, send_topic_to_telegram
from donationalerts.asyncio_api import Alert


load_dotenv()
db = connect_to_mongodb()
print(db)
donated_id = 0
source = 'Donation'

alert = Alert(os.getenv('TOKENDONATGTA') if Project == 'Gta' else os.getenv('TOKENDONATSMESH'))

@alert.event()
async def new_donation(event):
    try:
        user = event.username
        amount = event.amount
        message = event.message
        currency = event.currency

        if user is None:
            user = "Аноним"

        donation_info = f'''
{user} задонатил {amount} {currency}
Сообщение: {message}'''

        await send_donated(donation_info)
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

        requestor_name = f'Донатер {user}'

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
                        await add_mashup(db, requestor, donated_id, source, 3, eng_speaker, url)
                    else:
                        print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")
                else:
                    print("ОШИБКА! НЕОБХОДИМО РУЧНОЕ ДОБАВЛЕНИЕ")


            elif FinalAmount >= DonatedTopicSumRub and DonatEnableTopics:
                print('Тема задоначена')
                
                if message == "":
                    return
                
                if message.lower().startswith("/тема"):
                    message = message[6:]

                if await filt(message):
                    await send_filter_error(message, requestor_name, requestor_id, source, 0, False)
                    return
                
                message, style_content = await check_topic_style(message)

                topic_id = await add_topic(db, requestor_name, "", requestor_id, source, 3, message, style_content)
                await send_topic_to_telegram(message, style_content, requestor_name, requestor_id, source, 3, str(topic_id), False)

            
            elif FinalAmount == DonatedInteractionOneSumRub and DonatEnableInteractionOne:
                print('Интерактив 1')
                if message.lower().startswith("/бандит"):
                    if await filt(user):
                        await send_filter_error(user, requestor_name, requestor_id, source, 0, False)
                        return    
                    await add_interaction(db, "donater", user)

                elif message.lower().startswith("/локация"):
                    await add_interaction(db, "location", user)

                elif message.lower().startswith("/драка"):
                    message = message[6:].strip()
                    parameter = ""
                    pattern = r"^\s*(\w+)?\s*(\w+)?\s*$" #паттерн двух имён
                    match = re.match(pattern, message)
                    if match:
                        name1, name2 = match.groups()
                        name1 = name1.upper() if name1 else None
                        name2 = name2.upper() if name2 else None
                        if (name1 and name1 in valid_speakers) and (name2 and name2 in valid_speakers):
                            parameter = f"{name1} {name2}"
                    await add_interaction(db, "fight", parameter)


    except KeyError as e:
        print(f"Error handling message: Missing key {e}")
    except Exception as e:
        print(f"Error handling message: {e}")
