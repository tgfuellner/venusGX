#! /usr/bin/python3

# Läuft auf hassbian
# Liest von N/0c1c57127018/system/0/Dc/Battery/Soc
#  und schreibt int Value nach openWB/set/lp/2/%Soc
#  was der openWB Ladepunkt dann darstellt

# Mit /etc/mosquitto/conf.d/bridgeToVictron.conf
#  connection bridgeVictron
#  address 192.168.0.181:1883
#  # topic # in 0
#  #topic N/0c1c57127018/system/0/Dc/Battery/Soc in 0 openWB/set/lp/2/%Soc/ N/0c1c57127018/system/0/Dc/Battery/Soc/
#  topic N/0c1c57127018/system/0/Dc/Battery/Soc in 0 N/0c1c57127018/system/0/Dc/Battery/Soc openWB/set/lp/2/%Soc

# Deploy dieses Script mit:
# scp mqttSocRelay.py pi@192.168.0.53:/home/pi/bin/mqttSocRelay.py

import paho.mqtt.client as paho
import time
import json
import signal
import atexit
import os

broker = "localhost"

def cleanup(*args):
    client.disconnect()
    client.loop_stop()
    print("Clean End")
    os._exit(0)


def on_message(client, userdata, message):
    m = str(message.payload.decode("utf-8")) 
    # print("received message =", m)
    try:
        d = json.loads(m)
        soc = int(round(float(d["value"])))
        client.publish("openWB/set/lp/2/%Soc", soc)
        print(soc)
    except json.decoder.JSONDecodeError:
        pass
    except BaseException as err:
        print(type(err), err)



client = paho.Client("SocRelay")

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
atexit.register(cleanup)

client.on_message=on_message

client.connect(broker)
client.loop_start()

client.subscribe("N/0c1c57127018/system/0/Dc/Battery/Soc")

while True:
    time.sleep(10)

