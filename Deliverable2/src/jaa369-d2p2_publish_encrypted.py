import paho.mqtt.client as mqtt
import time
import json
from cryptography.fernet import Fernet

# ---------------------------------
broker = "broker.hivemq.com"        
# ---------------------------------
# broker = "broker.emqx.io"           
# ---------------------------------
# broker = "test.mosquitto.org"       
# ---------------------------------
# broker = "mqtt.eclipseprojects.io"     
# ---------------------------------


def publish(client):
    global PACKETS_SENT
    global FLAG_EXIT
    PACKETS_SENT = 0
    FLAG_EXIT = False
    while not FLAG_EXIT:
        if PACKETS_SENT >= 30:
            FLAG_EXIT = True
            client.loop_stop()
        print(f"Published {PACKETS_SENT} packets to topic `jaa369_publish`")
        # Encode message as JSON which includes the message with a number and
        # a nicely formatted timestamp
        message = json.dumps({"message": f"Hello, World! {PACKETS_SENT}",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
        # Publish the message to the topic jaa369_publish

        # PART 1 Q4a: Show in your code how to change QoS
        # PART 1 Q4b: Show in your code how to change retain
        # PART 2 Q6: Encrypt the message using AES-256

        # Generate a key for AES-256
        key = Fernet.generate_key()
        # Store the key in a file
        with open("jaa369-d2p2-key.key", "wb") as file:
            file.write(key)
            file.close()

        # Create a Fernet instance with the key
        f = Fernet(key)
        # Encrypt the message
        encrypted_message = f.encrypt(message.encode())
        # Publish the encrypted message
        result = client.publish("jaa369_publish", encrypted_message, qos = 0, retain = False)
        status = result[0]

        if status == 0:
            print(f"Send `{message}` to topic `jaa369_publish`")
            print(f"Encrypted message: {encrypted_message}")
            PACKETS_SENT += 1
        else:
            print(f"Failed to send message to topic `jaa369_publish`")
        time.sleep(1)


def run():
    global PACKETS_SENT
    client = mqtt.Client("jaa369_publish")
    client.connect(broker)
    client.loop_start()
    time.sleep(1)
    if client.is_connected():
        print(f"Connected to {broker}")
        publish(client)
    else:
        print(f"Connection to {broker} failed")
        client.loop_stop()
        exit()
    
        


if __name__ == "__main__":
    run()


    