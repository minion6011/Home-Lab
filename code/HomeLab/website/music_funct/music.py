import pytubefix
from pytubefix.cli import on_progress


def download_youtube(url):
	if url.startswith("https://youtu.be/"):
		url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=")
	else:
		url = url
	yt = pytubefix.YouTube(url, on_progress_callback = on_progress, client="WEB")
	file_name = f"{yt.title}.mp3"
	yt.streams.first().download(filename=file_name)
