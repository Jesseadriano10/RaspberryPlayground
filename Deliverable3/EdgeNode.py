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
from tabulate import tabulate
import threading
import logging
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
    def flash(self,pin: int) -> None:
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)

class MQTTClient:
    def __init__(self, broker_name: str, command_callback=None) -> None:
        self.broker_name: str = broker_name
        self.client = mqtt.Client("jaa369_d3")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_name, keepalive=60)
        self.command_callback = command_callback

    
    def on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        logging.info(f"Connected with result code {rc}")
        
        self.client.subscribe("parking/displayBoard/")
        self.client.subscribe("parking/system/")
    
    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        # Handle incoming MQTT messages and act on them if needed
        # On message received, handle displayBoard content to console
        logging.info(f"Received `{msg.payload}` from topic `{msg.topic}`")
        payload = json.loads(msg.payload)
        if msg.topic == "parking/displayBoard/":
            print(self.format_displayBoard(payload))
        elif msg.topic == "parking/system/":
            # Decode contents of the message and send to the console
            # and update command var
            if 'command' in payload and self.command_callback:
                self.command_callback(payload['command'])

            
            
    
    def format_displayBoard(self, payload: dict) -> str:
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
        logging.info(f"Published `{payload}` to topic `{topic}`")
        

class ParkingSpot:
    def __init__(self) -> None:
        self.spots = [0,0,0,0,0] # 5 Parking spots
        self.occupied = 0 # Number of occupied spots
        
    def update(self, spot: int ) -> None:
        if (spot < 0 or spot > 4):
            logging.error("Invalid spot number")
        elif self.spots[spot] == 1:
            logging.info(f"Spot {spot} is already occupied")
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
        self.command_lock = threading.Lock()
        self.running = True # Control execution of threads
        self.mqtt_client = MQTTClient(broker, command_callback=self.handle_new_command)
        self.parkingSpot = ParkingSpot()
        self.RGB_RED: int = light_pins[0]
        self.RGB_GREEN: int = light_pins[1]
        self.RGB_BLUE: int = light_pins[2]
        self.command = None

    def handle_new_command(self, new_command: str) -> None:
        with self.command_lock:
            self.command = new_command

    def serverSide(self) -> None:
        while self.running:
            if self.parkingSpot.isFull():
                logging.warning("Parking lot is full")
            spot = self.getInput()
            if spot >= 0 and spot <= 4:
                self.parkingSpot.update(spot)
                logging.info(f"Parking in spot {spot}")
                self.readSensorAndPublish()
                logging.info(f"Sensor value: {self.dataSensor.read()}")
            elif spot == 'c':
                spot = int(input("Enter the spot to clear: "))
                self.parkingSpot.clear(spot)
            elif spot == 'q':
                logging.info("Exiting App: User pressed q...")
                sys.exit(0)
            time.sleep(1)
    """
    Client side of the application
    Deals with displaying contents of the MQTT messages from the 
    QT side of the application to the console
    """
    def clientSide(self) -> None:
        while self.running:
            with self.command_lock:
                if self.command == "WARN ON":
                    self.lights.flash(self.RGB_RED)
                elif self.command == "WARN OFF":
                    self.lights.off(self.RGB_RED)
                self.command = None
            time.sleep(1)

        
    def run(self) -> None:
        self.mqtt_client.start()
        # Two threads to run the server and client side of the application
        server_thread = threading.Thread(target=self.serverSide)
        client_thread = threading.Thread(target=self.clientSide)
        server_thread.start()
        client_thread.start()
        try:
            while self.running:
                # Main thread can continue to run or wait
                # for other threads to finish
                time.sleep(1)

        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Exiting App...")
            self.running = False # Stop the threads
            GPIO.cleanup()
            sys.exit(0)
        finally:
            server_thread.join()
            client_thread.join()
            self.mqtt_client.stop()
            logging.info("Exiting App...")
            GPIO.cleanup()

            sys.exit(0)

    
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    edgeNode = EdgeNode(light_pins, adcAddr, broker)
    edgeNode.run()
    GPIO.cleanup()
    sys.exit(0)