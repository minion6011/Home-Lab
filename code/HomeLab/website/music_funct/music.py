import pytubefix
from pytubefix.cli import on_progress
import os 

def download_youtube(url):
	if url.startswith("https://youtu.be/"):
		url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=")
	yt = pytubefix.YouTube(url, on_progress_callback = on_progress)
	file_name = f"{yt.title}.mp3"
	path = os.path.abspath(os.getcwd()) + "/website/music_funct/"
	yt.streams.first().download(filename=file_name, output_path=path)
