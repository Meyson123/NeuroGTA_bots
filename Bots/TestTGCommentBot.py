from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, ChannelPrivateError

api_id = ''
api_hash = ''
phone_number = ''
channel_username = ''
message_to_post = 'Ваше сообщение'

discussion_group = ''
comment = 'Ваш комментарий'

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    # Проверяем, что сообщение не является ответом на другое сообщение
    if not event.message.reply_to_msg_id:
        print(f'Новый пост: {event.message.text}')
        try:
            # Отправка комментария в обсуждение
            await client.send_message(discussion_group, f'{comment} на пост: {event.message.text}')
            print(f'Комментарий отправлен в обсуждение: {discussion_group}')
        except ChannelPrivateError:
            print('Ошибка: Доступ к обсуждению запрещён.')

async def main():
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input('Введите код подтверждения: ')
        try:
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input('Введите двухфакторный пароль: ')
            await client.sign_in(password=password)

    print('Бот запущен и отслеживает новые сообщения.')
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
