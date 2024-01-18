import paho.mqtt.client as mqtt
import time

broker = "broker.hivemq.com"
client = mqtt.Client("jaa369_publish")

client.connect(broker)
send = 30
count = 0
while (True):
    send = 30
    client.publish("jaa369_part1", 30 -  count)
    time.sleep(1)
    if count == send:
        break 
