from flask import Flask, render_template, request, redirect, send_from_directory, send_file
from markupsafe import escape, Markup
import os
import json
import signal
import time
import threading
import website.music_funct.music as musiclib
from urllib.parse import unquote
import psutil
import film_stream as film_py
import api_tool as api_py
import shutil

# - Mini Config
img_ext = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.gif')
video_ext = ('.webm', '.mkv', '.vob', '.ogv', '.gifv', '.mng', '.mov', '.avi', '.amv', '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m4v', '.svi')
audio_ext = ('.mp3', '.flac', '.aac', '.ogg', '.wav')
editor_ext = ('.txt', '.py', '.js', '.bat', ".json", ".css", ".xml", ".html")

# - Code
with open("app_config.json") as f:
	data_config = json.load(f)

with open("users.json") as f:
	users_dict = json.load(f)

app = Flask(__name__, static_folder="website", template_folder="website")
PID = os.getpid()

@app.context_processor
def handle_context():
	def check_file(filename):
		if filename.endswith(img_ext): return "image"
		elif filename.endswith(video_ext): return "video"
		elif filename.endswith(audio_ext): return "audio"
		elif filename.endswith(editor_ext): return "edit"
		else: return "unclass"
	return dict(os=os, check_file=check_file)

# - Esp32 Integration
if data_config["ESP32_integration"] == "True":
	# - Temperature
	global data_temp
	data_temp = {"temperature": "??", "humidity":"??", "time":"??"}
	
	@app.route('/esp32_data', methods=['POST'])
	def esp32_data():
		global data_temp
		data_temp = request.get_json(force=True)
		data_temp["time"] = time.strftime('%H:%M')
		return "Data accepted", 200
	
	@app.route("/esp32_get")
	def esp32_get():
		global data_temp
		return f"<h1>🌡️ Temperatura: {data_temp['temperature']}°C<br>💧 Umidità: {data_temp['humidity']}%<br>🕐 Last Info: {data_temp['time']}</h1>"
	# - Display LCD (x16)
	@app.route("/esp32_display")
	def esp32_display():
		text = f"{time.strftime('%H:%M %d/%m/%Y')}"
		return {"text": text}


# - Home
@app.route("/")
@app.route("/index")
def index():
	import platform
	if "Windows" in platform.system():
		cpu = "??"
		disk = psutil.disk_usage('/').percent
		ram = round(psutil.virtual_memory().percent, 1)
	else:
		from gpiozero import CPUTemperature
		try: cpu = int(CPUTemperature().temperature)
		except: cpu = "??"
		disk = psutil.disk_usage('/').percent
		ram = round(int(psutil.virtual_memory().used / 1083692.37333) / 7809 * 100, 1)
	return render_template('index.html', cpu_temp=cpu, disk_usage=disk, ram_usage=ram, esp32_int=data_config["ESP32_integration"])

@app.route('/execute_command', methods=['POST'])
def execute_command():
	process = os.popen(request.form['command'])
	response = process.read()
	process.close()
	return render_template("command_response.html", command_response=response)

# - Update
def shutdown_server(pid):
	time.sleep(3)
	os.kill(pid, signal.SIGINT)

@app.route('/update')
def update():
	pid = os.getpid()
	if pid == PID:
		threading.Thread(target=shutdown_server, args=(pid,)).start()
		return render_template("shutdown.html")
		
# - Music
@app.route('/music')
@app.route('/music/<status>')
def music(status=" "):
	song_dict = {}
	files = os.listdir("website/music_funct")
	for file in files:
		if file.endswith(".mp3"):
			song_dict[file[:-4]] = f"music_funct/{file}"
	if status == "success": status = "<p style='font-weight: 600; color: green;'>✅ Download eseguito con successo ✅</p>"
	if status == "fail": status = "<p style='font-weight: 600; color: red;'>❌ Si è verificato un errore eseguendo il download ❌</p>"
	return render_template('music.html', status=Markup(status), song_dict=song_dict)

@app.route('/process_song', methods=['POST'])
def process():
	url = str(request.form['url'])
	if not "playlist" in url:
		if "youtu" in url:
			musiclib.download_youtube(url)
			return redirect("/music/success")
		else:
			return redirect("/music/fail")
	else:
		return redirect("/music/fail")

@app.route('/delete_song/<song_name>')
def delete_song(song_name):
	song_name = unquote(song_name)
	music_path = os.path.abspath("website/music_funct")
	os.remove(f"{music_path}/{song_name}.mp3")
	#return redirect("/music")
	return {}

# - Api Tool
@app.route('/api_tool')
def api_tool():
	return render_template('api.html')

@app.route('/send_request', methods=['POST'])
def api_send_request():
	r = api_py.api_send(request.form['type'], request.form['url'], request.form['json'], request.form['headers'])
	return render_template("response.html", status_code=r["code"], json_response=r["json"])

# - Film

@app.route('/film')
def film_index():
	return render_template('film.html')

@app.route('/film_search', methods=['POST'])
def film_search():
	name = request.form['film_name']
	film_list = film_py.search_film(name)
	return render_template('film_search.html', film_dict=film_list)

@app.route('/film_iframe', methods=['POST'])
def film_iframe():
	id = request.form['film_id']
	html_value = film_py.find_iframe(id)
	return render_template('film_iframe.html', value=Markup(html_value))


# - Edit File

def conv_chr(input_string):
	import re
	import html
	input_string = html.unescape(input_string)
	input_string = input_string.replace("\\", "\\")
	input_string = input_string.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
	input_string = input_string.replace('"', '\"').replace("'", "\'")
	return input_string


@app.route('/editor_file', methods=['POST'])
def editor_file():
	user = request.form['user']
	password = request.form['password']
	file_name = request.form['filename']
	path_folder = request.form['path']
	if user in users_dict:
		if password == users_dict[user]["password"]:
			f = open(os.path.join(path_folder, file_name), "r", encoding="utf-8")
			code = conv_chr(f.read())
			f.close
			return render_template('editor.html', user_name=user, auth=users_dict[user]["password"], path=path_folder, filename=file_name, code_old=code)
	return redirect("/login/fail")

@app.route('/edit_file', methods=['POST'])
def edit_file():
	user = request.form['user']
	password = request.form['password']
	file_name = request.form['file_name']
	path_folder = request.form['path']
	code_new = request.form['code_new']
	if user in users_dict:
		if password == users_dict[user]["password"]:
			f = open(os.path.join(path_folder, file_name), "w")
			f.write(code_new)
			f.close()
			path_back = "None"
			if path_folder == "None": path_folder = users_dict[user]["path"]
			if not path_folder == "None" and not path_folder == users_dict[user]["path"]: path_back = os.path.dirname(path_folder)
			user_files = sorted(os.listdir(path_folder), key=str.lower)
			return render_template('user.html', user_name=user, files=user_files, auth=users_dict[user]["password"], path=path_folder, home_path=users_dict[user]["path"], back_path=path_back)
	return redirect("/login/fail")


# - Login

@app.route('/login')
@app.route('/login/<status_login>')
def login_index(status_login=None):
	value_return = " "
	if status_login == "fail":
		value_return = "<h2 style='color: red; margin-bottom: 0px'>Password Errata</h2>"
	return render_template("login.html", login_status=Markup(value_return))


@app.route('/user_panel', methods=['POST'])
def user_panel():
	user = request.form['user']
	password = request.form['password']
	path_folder = request.form['path']
	if user in users_dict:
		if password == users_dict[user]["password"]:
			path_back = "None"
			if path_folder == "None": path_folder = users_dict[user]["path"]
			if not path_folder == "None" and not path_folder == users_dict[user]["path"]: path_back = os.path.dirname(path_folder)
			user_files = sorted(os.listdir(path_folder), key=str.lower)
			return render_template('user.html', user_name=user, files=user_files, auth=users_dict[user]["password"], path=path_folder, home_path=users_dict[user]["path"], back_path=path_back)
	return redirect("/login/fail")

def get_files(dir):
	response_dict = {}
	files = os.listdir(dir)
	for file in files:
		#if os.path.isfile(os.path.join(dir, file)):
		response_dict[file] = os.path.join(dir, file)
	return response_dict



@app.route('/upload_file', methods=['POST'])
def upload_file():
	user = request.form['user']
	password = request.form['password']
	path = request.form['path']
	uploaded_files = request.files.getlist("file")
	if user in users_dict:
		if password == users_dict[user]["password"]:
			for uploaded_file in uploaded_files:
				file_list = get_files(path)
				if not uploaded_file in file_list:
					uploaded_file.save(os.path.join(path, uploaded_file.filename))
			return redirect("/user_panel", code=307)
	return redirect("/login/fail")


@app.route('/delete_file', methods=['POST'])
def delete_file():
	user = request.form['user']
	password = request.form['password']
	path = request.form['path']
	file = request.form['filename']
	
	if user in users_dict:
		if password == users_dict[user]["password"]:
			file_list = get_files(path)
			if file in file_list:
				if os.path.isfile(os.path.join(path, file)):
					os.remove(os.path.join(path, file))
				else:
					shutil.rmtree(os.path.join(path, file), ignore_errors=True)
				return redirect("/user_panel", code=307)	

	return redirect("/login/fail")


@app.route('/download_file', methods=['POST'])
def download_file():
	user = request.form['user']
	password = request.form['password']
	path = request.form['path']
	file = request.form['filename']
	
	if user in users_dict:
		if password == users_dict[user]["password"]:
			file_list = get_files(path)
			if file in file_list:
				return send_from_directory(path, file, as_attachment=True)
	return redirect("/login/fail")


@app.route('/add_folder', methods=['POST'])
def add_folder():
	user = request.form['user']
	password = request.form['password']
	path = request.form['path']
	
	if user in users_dict:
		if password == users_dict[user]["password"]:
			file_list = get_files(path)
			i = 0
			for file in file_list:
				if not os.path.isfile(os.path.join(path, file)):
					if "Nuova Cartella" in file:
						i = i + 1
			if i == 0:
				os.mkdir(os.path.join(path, "Nuova Cartella"))
			else:
				os.mkdir(os.path.join(path, f"Nuova Cartella ({i})"))
			return redirect("/user_panel", code=307)
	return redirect("/login/fail")


@app.route('/get_image', methods=['POST'])
def get_image():
	filename = request.form.get('filename')
	user = request.form.get('user')
	password = request.form.get('password')
	path = request.form.get('path')
	if user in users_dict:
		if password == users_dict[user]["password"]:
			return send_from_directory(path, filename, as_attachment=False)
	return redirect("/login/fail")

@app.route('/rename_file', methods=['POST'])
def rename_file():
	user = request.form['user']
	password = request.form['password']
	path = request.form['path']
	file_old = request.form['filename_old']
	file_new = request.form['filename_new']
	
	
	if user in users_dict:
		if password == users_dict[user]["password"]:
			file_list = get_files(path)
			if file_old in file_list:
				if not file_new in file_list:
					old_name = os.path.join(path, file_old)
					new_name = os.path.join(path, file_new)
					os.rename(old_name, new_name)
			return redirect("/user_panel", code=307)
	return redirect("/login/fail")


if __name__ == '__main__':
	# - Get local ip
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
	# - WebHook
	api_py.api_send("POST", data_config["discord_webhook"], {"content":f"> Local Host: http://{ip}:5000"})
	# - App Run
	app.run(host="0.0.0.0", debug=False)
