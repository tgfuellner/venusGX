#! /usr/bin/python3

# Zum Testen
# mosquitto_sub -h 192.168.0.181 -t "#" -v

# Läuft auf hassbian
# Liest von N/0c1c57127018/system/0/Dc/Battery/Soc
#  und schreibt int Value nach openWB/set/lp/2/%Soc
#  was der openWB Ladepunkt dann darstellt

# Stabiler Aufruf: while ./mqttSocRelay.py;do echo restart; done
# Besser crontab um 7:45
#   45 7 * * * killall -q mqttSocRelay.py; /home/pi/bin/mqttSocRelay.py > /dev/null 2>&1

# Diese Version läuft ohne bridge!
#
# Jetzt nicht mehr notwendig:
# Mit /etc/mosquitto/conf.d/bridgeToVictron.conf
#  connection bridgeVictron
#  address 192.168.0.181:1883
#  # topic # in 0
#  #topic N/0c1c57127018/system/0/Dc/Battery/Soc in 0 openWB/set/lp/2/%Soc/ N/0c1c57127018/system/0/Dc/Battery/Soc/
#  topic N/0c1c57127018/system/0/Dc/Battery/Soc in 0 N/0c1c57127018/system/0/Dc/Battery/Soc openWB/set/lp/2/%Soc

import paho.mqtt.client as paho
import time
import json
import signal
import atexit
import os

#broker = "localhost"   # Geht nur bei funktionierender bridge
broker = "192.168.0.181"

def closeClients():
    client.disconnect()
    client.loop_stop()
    clientLocal.disconnect()
    clientLocal.loop_stop()

def cleanup(*args):
    closeClients()
    print("cleanup")
    os._exit(1)


def on_message(client, userdata, message):
    m = str(message.payload.decode("utf-8")) 
    # print("received message =", m)
    try:
        d = json.loads(m)
        soc = int(round(float(d["value"])))
        clientLocal.publish("openWB/set/lp/2/%Soc", soc)
        print(soc)
    except json.decoder.JSONDecodeError:
        pass
    except BaseException as err:
        print(type(err), err)



client = paho.Client("SocRelay")
clientLocal = paho.Client("SocWriter")

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
#atexit.register(cleanup)

client.on_message=on_message

client.connect(broker)
client.loop_start()
clientLocal.connect("localhost")
clientLocal.loop_start()

client.subscribe("N/0c1c57127018/system/0/Dc/Battery/Soc")
# print(client.subscribe("N/0c1c57127018/battery/258/Soc"))
# print(client.subscribe("N/0c1c57127018/vebus/261/Soc"))

#while True:
secondsPerDay = 86400
time.sleep(secondsPerDay)

closeClients()
