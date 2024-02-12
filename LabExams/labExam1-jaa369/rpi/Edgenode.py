# Jesse Aguirre
# CME466: Lab Exam 1
# 2024-02-12

import RPi.GPIO as GPIO
import time
import PCF8591 as ADC
import numpy as np
import matplotlib.pyplot as plt
import sys
import paho.mqtt.client as mqtt
import json
from typing import Any, Dict, List, Tuple
import logging
import base64
import cv2

class MQTTClient:
    def __init__(self, broker: str) -> None:
        self.broker: str = broker
        self.client: mqtt.Client = mqtt.Client("jaa369RPi-exam1")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.connect(self.broker, keepalive=60)
        self.client.loop_start()
    
    def on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        logging.info("Connected with result code "+str(rc))
        client.subscribe("jaa369/exam1/channel")
        client.subscribe("jaa369/exam1/ack")
        # TODO: Add additional topics to subscribe to here

    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        # Only receive on ack topic
        if msg.topic == "jaa369/exam1/ack":
            print(f"Received `{msg.payload}` from `{msg.topic}` topic")
        

    def start(self) -> None:
        self.client.loop_start()
    
    def stop(self) -> None:
        self.client.loop_stop()

    # QOS 1: At least once, QOS 0: At most once
    def publish(self, topic: str, payload: json) -> None:
        # TODO: Maybe set retain to True
        self.client.publish(topic, payload, qos= 0, retain= False)
        logging.info(f"Published `{payload}` to `{topic}` topic")
    

class Edgenode:
    def __init__(self, broker: str) -> None:
        
        self.mqtt: MQTTClient = MQTTClient(broker)
        # TODO: MAYBE ADD LIGHT VARIABLES FOR READIBILITY
        self.fileImage = ""

        

    def run(self) -> None:
        self.mqtt.start()
        while True:
            # TODO: Add the logic to do something...
            try:
                # Send a message with command and message
                # 0: default display
                # 1: Happy Birthday
                # 2: Saskatoon Shines

                command = int(input("Enter a command: "))
                if command == 0:
                    self.mqtt.publish("jaa369/exam1/channel", json.dumps({"command": 0}))
                elif command == 1:
                    self.fileImage = "image1.png"
                    self.scale_image(self.fileImage, 100)
                    self.mqtt.publish("jaa369/exam1/channel", json.dumps({"command": 1}))
                elif command == 2:
                    self.fileImage = "image2.png"
                    self.scale_image(self.fileImage, 50)
                    self.mqtt.publish("jaa369/exam1/channel", json.dumps({"command": 2}))
                else:
                    print("Invalid command")
            except KeyboardInterrupt:
                self.mqtt.stop()
                GPIO.cleanup()
                logging.info("Exiting...")
                sys.exit()
        
    def encode_image(self, image: str) -> str:
        with open(image, "rb") as image2bytes:
            return base64.b64encode(image2bytes.read()).decode("utf-8")
    
    def scale_image(self, image: str, scale_percent: float) -> None:
        img = cv2.imread(image)
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite(image, resized)


if __name__ == "__main__":

    try:
        broker = sys.argv[1]
    except IndexError:
        broker = "test.mosquitto.org"

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    node = Edgenode(broker)
    node.run()
    GPIO.cleanup()
    sys.exit(0)
    