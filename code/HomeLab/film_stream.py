from scuapi import API
import json

with open("app_config.json") as f:
	data_config = json.load(f)

base_url = data_config["streamingcommunity_url"]

def search_film(name: str):
  sc = API(base_url)
  film_list = sc.search(name)
  film_dict = {}
  for film in film_list:
    if film_list[film]["type"] == "movie":
      film_dict[film] = film_list[film]["id"]
  if film_dict == {}:
    film_dict["Nessun Risultato"] = "None"
  return film_dict
    
def find_iframe(id: str):
  if not id == "None":
    sc = API(base_url)
    iframe, m3u_playlist_url = sc.get_links(id)
    return f'<a href="{iframe}" target="_blank" class="restart-button">Link del film</a>'
  else:
    return '<h2 style="font-weight: 600; color: red;">❌ No results found ❌</h2>'
