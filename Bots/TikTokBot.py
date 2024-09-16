from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, ShareEvent,\
    GiftEvent, LikeEvent, LiveEndEvent, LivePauseEvent, FollowEvent, SubscribeEvent
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb, add_interaction
from Mongodb.CountScripts import format_number
from TelegramSender import sending_to_tg
from PrintColored import print_colored
from AvatarSaver import save_avatar
db = connect_to_mongodb()
id = "@sekira.axx7"

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id=id)

user_shares = {}
shares_for_action = 1

user_likes = {}
likes_for_action = 200

likes_treshold = 3000
total_likes = 0
last_total_likes = 0
first_like = True

gift_switch = {
    "Rose": lambda: add_interaction(db, "gift", "Rose"),
    "Rosa": lambda: add_interaction(db, "gift", "Rose"),
    "Heart Me": lambda: add_interaction(db, "gift", "Fire"),
    "Fire": lambda: add_interaction(db, "gift", "Fire")
}

# Listen to an event with a decorator!
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")

@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print(f"Fuck! Disconnect")
    await reconnect()

async def reconnect():
    client: TikTokLiveClient = TikTokLiveClient(unique_id=id)
    await asyncio.sleep(5)  # Wait for 5 seconds before trying to reconnect
    try:
        await client.run()  # Try to reconnect
    except Exception as e:
        print(f"Reconnection failed: {e}. Retrying...")
        await reconnect()  # Retry reconnecting

@client.on(LiveEndEvent)
async def on_comment(event: LikeEvent) -> None:
    print(f"Стрим завершен / ошибка")
    await sending_to_tg(text="❗️ТТ СТРИМ ЗАВЕРШИЛСЯ❗️")

@client.on(LivePauseEvent)
async def on_comment(event: LivePauseEvent) -> None:
    print(f"Стрим на паузе / ошибка")
    await sending_to_tg(text="❗️ТТ СТРИМ НА ПАУЗЕ❗️")
    

@client.on(CommentEvent)
async def on_comment(event: CommentEvent) -> None:
    print_colored(f"{event.user.nickname} -> {event.comment}", "pink")

@client.on(FollowEvent)
async def on_sub(event: FollowEvent) -> None:
    print_colored(f"{event.user.nickname} подписался!", "green")

@client.on(SubscribeEvent)
async def on_subs(event: SubscribeEvent) -> None:
    print_colored(f"{event.user.nickname} подписался!", "blue") 

@client.on(ShareEvent)
async def on_share(event: ShareEvent) -> None:
    global user_shares
    print_colored(f"{event.user.nickname} поделился" ,"blue")
    user_id = event.user.unique_id
    if user_id not in user_shares:
        user_shares[user_id] = 0
    user_shares[user_id] += 1
    if user_shares[user_id] == shares_for_action:
        user_shares[user_id] = 0
        url = await save_avatar(user_id)
        await add_interaction(db, "avatar", url) 
        print_colored(f"{event.user.nickname} поделился стримом {shares_for_action} раз(а)!", "blue")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    #client.logger.info("Received a gift!")
    # Can have a streak and streak is over
    if event.gift.streakable and not event.streaking:
        print_colored(f"{event.user.unique_id} sent {event.repeat_count}x \"{event.gift.name}\"", "blue")
        if event.gift.name in gift_switch:
            await gift_switch[event.gift.name]()

    # Cannot have a streak
    elif not event.gift.streakable:
        print_colored(f"{event.user.unique_id} sent \"{event.gift.name}\"", "blue")
        if event.gift.name in gift_switch:
            await gift_switch[event.gift.name]()

@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    #print(await save_photo(event.user.avatar_thumb.url_list[0], event.user.unique_id))
    #print(event.user.avatar_thumb.url_list[0])
    #Салюты каждые likes_treshold лайков
    global first_like, last_total_likes, total_likes, likes_treshold

    if first_like:
        last_total_likes = event.total
        total_likes = event.total
        first_like = False

    total_likes = event.total

    if total_likes - last_total_likes > likes_treshold:
        last_total_likes = total_likes
        likes = await format_number(total_likes)
        print(f"{likes} лайков")
        await add_interaction(db, "likes", likes)

    #интерактив для каждого юзера 

    global user_likes, likes_for_action
    user_id = event.user.unique_id

    if user_id not in user_likes:
        user_likes[user_id] = {'like_count': 0}

    user_likes[user_id]['like_count'] += event.count
    print(f"{event.user.nickname} поставил {event.count} лайков. Всего от юзера: {user_likes[user_id]['like_count']}")

    if user_likes[user_id]['like_count'] >= likes_for_action:
        print(f"Юзер {event.user.nickname} поставил нужное кол-во лайков ({user_likes[user_id]['like_count']})")
        user_likes[user_id]['like_count'] = 0
        await add_interaction(db, "donater", event.user.nickname)

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    #client.logger.setLevel(LogLevel.INFO.value)
    client.run()
    