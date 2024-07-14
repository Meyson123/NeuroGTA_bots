from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Mongodb.BotsScripts import connect_to_mongodb, add_interaction

db = connect_to_mongodb()

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@neurogta")


# Listen to an event with a decorator!
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")


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


if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    #client.logger.setLevel(LogLevel.INFO.value)
    client.run()
    