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
from tabulate import tabulate
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
        self.client.subscribe("parking/displayBoard/")
        self.client.subscribe("parking/system/")
    
    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        # Handle incoming MQTT messages and act on them if needed
        # On message received, handle displayBoard content to console
        print(f"Received `{msg.payload}` from topic `{msg.topic}`")
        if msg.topic == "parking/displayBoard/":
            print(self.format_displayBoard(json.loads(msg.payload)))
        elif msg.topic == "parking/system/":
            # Decode contents of the message and send to the console
            # and update command var
            global command
            command = json.loads(msg.payload)
            print(f"Received `{command}` from topic `{msg.topic}`")
            
            
    
    def format_displayBoard(self, payload: json) -> str:
        # Format the displayBoard message
        headers = ["Message", "Timestamp"]
        data = [payload["message"], payload["timestamp"]]
        return tabulate(data, headers, tablefmt="grid", stralign="center")
    
    
    def start(self) -> None:
        self.client.loop_start()
    def stop(self) -> None:
        self.client.loop_stop()
        
    def publish(self, topic: str, payload: json) -> None:
        self.client.publish(topic, payload, qos=0, retain=False)
        print(f"Published `{payload}` to topic `{topic}`")
        

class ParkingSpot:
    def __init__(self) -> None:
        self.spots = [0,0,0,0,0] # 5 Parking spots
        self.occupied = 0 # Number of occupied spots
        
    def update(self, spot: int ) -> None:
        if (spot < 0 or spot > 4):
            raise ValueError("Invalid spot number")
        elif self.spots[spot] == 1:
            print(f"Spot {spot} is already occupied")
        self.spots[spot] = 1
        self.occupied = sum(self.spots)
    
    def isFull(self) -> bool:
        return self.occupied == 5
    
    def clear(self, spot: int) -> None:
        if (spot < 0 or spot > 4):
            raise ValueError("Invalid spot number")
        self.spots[spot] = 0
        self.occupied = sum(self.spots)
    

class EdgeNode:
    def __init__(self, light_pins: Tuple[int], adcAddr: int, broker: str ) -> None:
        self.dataSensor = ADCSensor(adcAddr)
        self.lights = WarningLight(light_pins)
        self.mqtt_client = MQTTClient(broker)
        self.parkingSpot = ParkingSpot()
        self.RGB_RED: int = light_pins[0]
        self.RGB_GREEN: int = light_pins[1]
        self.RGB_BLUE: int = light_pins[2]
        global command
        command: str = ""


    def serverSide(self) -> None:
        if self.parkingSpot.isFull():
            print("Parking lot is full")
        else:
            spot = self.getInput()
            if spot >= 0 and spot <= 4:
                self.parkingSpot.update(spot)
                self.readSensorAndPublish()
            elif spot == 'c':
                spot = int(input("Enter the spot to clear: "))
                self.parkingSpot.clear(spot)
            elif spot == 'q':
                print("Exiting app")
                sys.exit(0)
    """
    Client side of the application
    Deals with displaying contents of the MQTT messages from the 
    QT side of the application to the console
    """
    def clientSide(self) -> None:
        global command
        if command == "WARN ON":
            self.lights.flash(self.RGB_RED)
        elif command == "WARN OFF":
            self.lights.off(self.RGB_RED)
        

        
    def run(self) -> None:
        self.mqtt_client.start()
        try:
            while True:
                self.serverSide()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting App...")
        finally:
            self.mqtt_client.stop()
    
    def getInput(self) -> int:
        # Get the input from the user
        print("Enter the parking spot number to park in: \n")
        print("0: Spot 1\n")
        print("1: Spot 2\n")
        print("2: Spot 3\n")
        print("3: Spot 4\n")
        print("4: Spot 5\n")
        print("c: Clear a spot\n")
        print("q: Exit\n")
        spot = int(input())
        return spot
    
        
    def readSensorAndPublish(self) -> None:
        payload = {
            "sensorValue": self.dataSensor.read(),
            "parkingLotData": self.parkingSpot.spots,
            "occupiedSlots": self.parkingSpot.occupied,
            "isFull": self.parkingSpot.isFull()
        }
        self.mqtt_client.publish("parking/system/", json.dumps(payload))
        

if __name__ == "__main__":
    # Set up the GPIO
    GPIO.setmode(GPIO.BCM)
    
    # Set up the EdgeNode
    light_pins: Tuple[int] = (17, 18, 27) # Red, Green, Blue
    adcAddr = 0x48
    broker = sys.argv[1]
    edgeNode = EdgeNode(light_pins, adcAddr, broker)
    edgeNode.run()
    GPIO.cleanup()
    sys.exit(0)