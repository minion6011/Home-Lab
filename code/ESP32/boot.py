import time
from machine import I2C, Pin
from I2C_LCD import I2cLcd
import urequests as requests
import network
import dht

import gc 
# - Mini Config

GPIO_Pin = 25

Wifi_Data = [
    {"SSID":"", "Password": ""},
    ]


temperature_url = "http://209.25.141.16:3164/esp32_data"
time_url = "http://209.25.141.16:3164/esp32_display"
# - Code

i2c = I2C(scl=Pin(14), sda=Pin(13), freq=400000)
sensor = dht.DHT11(Pin(GPIO_Pin))

wlan = network.WLAN(network.WLAN.IF_STA)

def temp():
    sensor.measure()
    return sensor.temperature()

def humid():
    sensor.measure()
    return sensor.humidity()

def data_send(data_json: dict):
    try:
        r = requests.post(temperature_url, json=data_json)
        print(r.status_code)
    except Exception as e:
        print("Request Error: 'data_send()'")
        print(e)
        
def get_time():
    try:
        r = requests.get(time_url).json()
        return r["text"]
    except Exception as e:
        print("Request Error: 'get_time()'")
        print(e)

def do_connect():
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        for data in Wifi_Data:
            try:
                wlan.connect(data['SSID'], data['Password'])
                while not wlan.isconnected():
                    pass
                print("Connected")
            except:
                print("Undefined wifi")
    print('network config:', wlan.ipconfig('addr4'))


devices = i2c.scan()
if len(devices) == 0:
  print("No i2c device !")
else:
  for device in devices:
    print("I2C addr: "+hex(device))
    lcd = I2cLcd(i2c, device, 2, 16)

lcd.backlight_on()
lcd.move_to(0, 0)
lcd.putstr("Starting...")

time.sleep(1)


while True:
    data_dht = {"temperature": temp(), "humidity": humid()}
    
    lcd.move_to(0, 0)
    lcd.putstr(f"Tem {data_dht['temperature']}C Umid {data_dht['humidity']}%")
    if wlan.isconnected():
        data_send(data_dht)
        
        lcd.move_to(0, 1)
        lcd.putstr(get_time())
    else:
        lcd.move_to(0, 1)
        lcd.putstr("No Wi-fi")
        do_connect()
    
    time.sleep(15)
    gc.collect()
