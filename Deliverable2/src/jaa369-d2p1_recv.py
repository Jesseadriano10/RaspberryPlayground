from datetime import datetime
import paho.mqtt.client as mqtt
import time
import json
import logging

# ---------------------------------
# broker = "broker.hivemq.com"        
# ---------------------------------
# broker = "broker.emqx.io"           
# ---------------------------------
# broker = "test.mosquitto.org"       
# ---------------------------------
broker = "mqtt.eclipseprojects.io"     
# ---------------------------------


"""
Python to receive MQTT messages by subscribing to a topic named
jaa369_publish and parse the JSON message to print the message and
the timestamp as well as the time it took to receive the message
"""
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if str(rc) == "0" and client.is_connected():
        print(f"Connected to {broker} with result code {str(rc)}")
        client.subscribe("jaa369_publish", qos = 0, options = None, properties = None)
    else:
        print(f"Connection to {broker} failed with result code {str(rc)}")
        exit()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # Decode the message payload from JSON
    payload = json.loads(msg.payload)
    # Print the message and the timestamp in
    # Parse JSON to print to console and write to file
    message = payload["message"]
    timestamp = payload["timestamp"]
    # Calculate the time it took to receive the message
    time_received = datetime.now()
    time_diff = time_received - datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    print(f"Received `{message}` at {timestamp}. (Time taken: {time_diff.total_seconds()} seconds)")
    # Write the message and the timestamp to a file
    with open(f"jaa369-d2p1_recv-{broker}.txt", "a") as file:
        file.write(f"Received `{message}` at {timestamp}. (Time taken: {time_diff.total_seconds()} seconds)\n")
    
    if message.endswith("29") or message.endswith("30"):
        client.disconnect()
        client.loop_stop()
        exit()
                

def run():
    client = mqtt.Client("jaa369_subscribe")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    run()





    