from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "https://www.youtube.com/watch?v=qh0Ur786y30"
 
yt = YouTube(url, on_progress_callback = on_progress, use_po_token=True)

 
ys = yt.streams.get_highest_resolution()
ys.download()