from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, GiftEvent, LikeEvent
import sys
import os
import asyncio
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb, add_interaction
from Mongodb.CountScripts import format_number

db = connect_to_mongodb()
id = "@neurogta"

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id=id)

user_likes = {}

likes_treshold = 3000
total_likes = 0
last_total_likes = 0
first_like = True

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


@client.on(CommentEvent)
async def on_comment(event: CommentEvent) -> None:
    print(f"{event.user.nickname} -> {event.comment}")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    #client.logger.info("Received a gift!")
    # Can have a streak and streak is over
    if event.gift.streakable and not event.streaking:
        print(f"{event.user.unique_id} sent {event.repeat_count}x \"{event.gift.name}\"")
        if event.gift.name == "Rose" or event.gift.name == "Rosa":
            await add_interaction(db, "gift", "Rose")

    # Cannot have a streak
    elif not event.gift.streakable:
        print(f"{event.user.unique_id} sent \"{event.gift.name}\"")
        if event.gift.name == "Rose" or event.gift.name == "Rosa":
            await add_interaction(db, "gift", "Rose")

@client.on(LikeEvent)
async def on_like(event: LikeEvent):
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
    # global user_likes
    
    # user_id = event.user.unique_id

    # if user_id not in user_likes:
    #     user_likes[user_id] = {'like_count': 0}

    # user_likes[user_id]['like_count'] += event.count
    # print(f"{event.user.nickname} поставил {event.count} лайков. Всего от юзера: {user_likes[user_id]['like_count']}.  Общее количество: {event.total}")

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    #client.logger.setLevel(LogLevel.INFO.value)
    client.run()
    