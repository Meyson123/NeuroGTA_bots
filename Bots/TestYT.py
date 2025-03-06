from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
 
url = "https://www.youtube.com/watch?v=qh0Ur786y30"

script_directory = os.path.dirname(os.path.abspath(__file__))
 

try:
    yt = YouTube(url,on_progress_callback = on_progress)
    video = yt.streams.filter(only_audio=True).first()
except Exception as e:
    print("Произошла ошибка при скачивании видео")
    print(e)

