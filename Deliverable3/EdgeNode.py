# Jesse Aguirre
# CME466: Deliverable 2 Part 3
# 2024-01-25
import RPi.GPIO as GPIO
import time
import PCF8591 as ADC
import sys
import paho.mqtt.client as mqtt
import json
from typing import List, Tuple
import PCF8591 as ADC
class ADCSensor:
    """
    Sensor class
    PCF8591 ADC is connected to the RPi via I2C 
    
    """
    def __init__(self, addr: int) -> None:
        self.addr: int = addr
        ADC.setup(self.addr)
        
    # Read the sensor value    
    def read(self) -> int:
        return ADC.read(0)


class WarningLight:
    """
    WarningLight class
    Warning light is connected to 3 pins for each color (red, yellow, green)
    
    """
    def __init__(self, pins: Tuple) -> None:
        self.pins: Tuple = pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        
    # Turn the warning light on. Flash the light that was specified
    def on(pin: int) -> None:
        GPIO.output(pin, GPIO.LOW)
        
    # Turn the warning light off
    def off(pin: int) -> None:
        GPIO.output(pin, GPIO.HIGH)
    
    # Flash the warning light
    def flash(pin: int) -> None:
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)

class MQTTClient:
    def __init__(self, broker_name: str) -> None:
        self.broker_name: str = broker_name
        self.client = mqtt.Client("jaa369_d3")
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker_name, keepalive=60)
    
    def on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        print(f"Connected with result code {rc}")
        self.client.subscribe("parking/commands/#")
    
    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        # Handle incoming MQTT messages and act on them if needed
        pass
    
    def start(self) -> None:
        self.client.loop_start()
    def stop(self) -> None:
        self.client.loop_stop()
        
    def publish(self, topic: str, payload: json) -> None:
        self.client.publish(topic, payload, qos=0, retain=False)
        print(f"Published `{payload}` to topic `{topic}`")
    
class EdgeNode:
    def __init__(self, light_pins: Tuple[int], adcAddr: int, broker: str ) -> None:
        self.dataSensor = ADCSensor(adcAddr)
        self.lights = WarningLight(light_pins)
        self.mqtt_client = MQTTClient(broker)
        
    def run(self) -> None:
        self.mqtt_client.start()
        try:
            while True:
                self.readSensorAndPublish()
                time.sleep(1)
        finally:
            self.mqtt_client.stop()
    def readSensorAndPublish(self) -> None:
        sensorValue = self.dataSensor.read()
        print(f"Sensor value: {sensorValue}")
        self.mqtt_client.publish(f"Sensor Value: {sensorValue}")

if __name__ == "__main__":
    # Set up the GPIO
    GPIO.setmode(GPIO.BCM)
    
    # Set up the EdgeNode
    light_pins: Tuple[int] = (17, 18, 27)
    adcAddr = 0x48
    broker = sys.argv[1]
    edgeNode = EdgeNode(light_pins, adcAddr, broker)
    edgeNode.run()
    GPIO.cleanup()
    sys.exit(0)