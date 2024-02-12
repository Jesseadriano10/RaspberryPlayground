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

class ADCSensor:
    def __init__(self, addr: int) -> None:
        self.addr: int = addr
        ADC.setup(self.addr)
    
    def read(self) -> int:
        return ADC.read(0)

class LED:
    def __init__(self, pins: Tuple[int]) -> None:
        self.pins: Tuple[int] = pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        
    # Turn a light on. No color specified will turn all lights on
    def on(self, pin: int) -> None:
        if pin == None:
            for pin in self.pins:
                GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.LOW)
        
    # Turn the warning light off
    def off(self, pin: int) -> None:
        if pin == None:
            for pin in self.pins:
                GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.HIGH)

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
        client.subscribe("jaa369/{insert_topic_here}")
        # TODO: Add additional topics to subscribe to here

    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        logging.info(f"Received `{msg.payload}` from `{msg.topic}` topic")
        payload = json.loads(msg.payload)
        # TODO: Apply msg to the appropriate function

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
    def __init__(self, light_pins: Tuple[int], adcAddr: int, broker: str) -> None:
        self.sensor: ADCSensor = ADCSensor(adcAddr)
        self.light: LED = LED(light_pins)
        
        self.mqtt: MQTTClient = MQTTClient(broker)
        # TODO: MAYBE ADD LIGHT VARIABLES FOR READIBILITY
        self.fileImage = "image.jpg"

        

    def run(self) -> None:
        self.mqtt.start()
        while True:
            # TODO: Add the logic to do something...
            try:
                pass
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
    light_pins = (17, 18) # Add more pins if needed
    adcAddr = 0x48
    try:
        broker = sys.argv[1]
    except IndexError:
        broker = "broker.hivemq.com"

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    node = Edgenode(light_pins, adcAddr, broker)
    node.run()
    GPIO.cleanup()
    sys.exit(0)
    