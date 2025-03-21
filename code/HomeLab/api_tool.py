import requests
import traceback

def api_send(type, link, r_json=None, r_headers=None):
    try:
        if not r_json == None: r_json=dict(r_json)
        if not r_headers == None: r_headers=dict(r_headers)
        r = requests.request(method=type, url=link, json=r_json, headers=r_headers)
        return {"code":str(r.status_code),"json":str(r.json())}
    except requests.exceptions.JSONDecodeError:
        return {"code":str(r.status_code),"json":"None"}
    except Exception as e:
        return {"code":"Error","json":str(e)}
