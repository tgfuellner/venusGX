from time import sleep
import ssl
import json
import os
from paho.mqtt.client import Client 
from vrmCredentials import username
from vrmCredentials import password
from vrmCredentials import portal_id
 
mqtt_broker = "mqtt70.victronenergy.com"
bat_topic = "N/%s/system/0/Dc/Battery/Voltage" % portal_id
soc_topic = "N/%s/system/0/Dc/Battery/Soc" % portal_id
 
def on_message(client, userdata, message):
    val = json.loads(message.payload)
    print(message.topic)
    print("  "+str(message.payload))
    print("----")
    # print(val["value"])
    # client.loop_stop()
    # client.disconnect()
    # os._exit(0)

def on_BatVoltage(client, userdata, message):
    val = json.loads(message.payload)
    print("Vbatt = %s" % val["value"])
 
def on_Soc(client, userdata, message):
    val = json.loads(message.payload)
    print("SOC = %s" % val["value"])
 
 
def on_connect(client, userdata, rc, *args): 
    client.subscribe(bat_topic)
    client.subscribe(soc_topic)
    #client.subscribe("N/%s/+/+/ProductId" % portal_id)
    #client.subscribe("N/%s/#" % portal_id)
 
client = Client("P1")
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.username_pw_set(username, password=password)
client.connect(mqtt_broker, port=8883)
client.on_connect = on_connect
client.on_message = on_message
client.message_callback_add(bat_topic, on_BatVoltage)
client.message_callback_add(soc_topic, on_Soc)
 
client.loop_start()
 
while True:
    sleep(1)

