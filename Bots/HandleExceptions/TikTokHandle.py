from subprocess import Popen
import os
import sys
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from TelegramSender import sending_to_tg
from PrintColored import print_colored
script = Popen(["python", "Bots/TikTokBot.py"])
script.communicate()
if script.returncode != 0:
    asyncio.run(sending_to_tg(text="❗️ТТ БОТ ВЫЛЕТЕЛ❗️"))
    print_colored("FUCK", "red")
