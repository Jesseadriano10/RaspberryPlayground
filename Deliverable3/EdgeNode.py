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
import threading
import logging


class ADCSensor:
    """
    Sensor class for PCF8591 ADC connected to the Raspberry Pi via I2C.
    
    Attributes:
        addr (int): The address of the ADC.
    
    Methods:
        __init__(self, addr: int) -> None:
            Initializes the ADCSensor object.
        
        read(self) -> int:
            Reads the sensor value from the ADC.
    
    """
    def __init__(self, addr: int) -> None:
        self.addr: int = addr
        ADC.setup(self.addr)
        
    def read(self) -> int:
        """
        Reads the sensor value from the ADC.
        
        Returns:
            int: The sensor value read from the ADC.
        """
        return ADC.read(0)

class WarningLight:
    """
    WarningLight class
    Warning light is connected to 3 pins for each color (red, yellow, green)
    
    """
    def __init__(self, pins: Tuple[int]) -> None:
        """
        Initialize the WarningLight object.

        Args:
            pins (Tuple[int]): The pins to which the warning light is connected.
        """
        self.pins: Tuple[int] = pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        
    # Turn a light on. No color specified will turn all lights on
    def on(self, pin: int) -> None:
        """
        Turn on the warning light.

        Args:
            pin (int): The pin number of the light to turn on. If None, all lights will be turned on.
        """
        if pin == None:
            for pin in self.pins:
                GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.LOW)
        
    # Turn the warning light off
    def off(self, pin: int) -> None:
        """
        Turn off the warning light.

        Args:
            pin (int): The pin number of the light to turn off. If None, all lights will be turned off.
        """
        if pin == None:
            for pin in self.pins:
                GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.HIGH)
    
    # Flash the warning light
    def startFlash(self,pin: int) -> None:
        """
        Start flashing the warning light.

        Args:
            pin (int): The pin number of the light to flash.
        """
        self.shouldFlash = True
        self.flash_thread = threading.Thread(target=self.flash, args=(pin,))
        self.flash_thread.start()
    
    def flash(self, pin: int) -> None:
        """
        Flash the warning light.

        Args:
            pin (int): The pin number of the light to flash.
        """
        while self.shouldFlash:
            self.on(pin)
            time.sleep(0.5)
            self.off(pin)
            time.sleep(0.5)
    
    def stopFlash(self) -> None:
        """
        Stop flashing the warning light.
        """
        self.shouldFlash = False
        self.off(None)
        self.flash_thread.join()

class MQTTClient:
    """
    A class representing an MQTT client.

    Args:
        broker_name (str): The name of the MQTT broker.
        command_callback (callable, optional): A callback function to handle incoming commands.

    Attributes:
        broker_name (str): The name of the MQTT broker.
        client (mqtt.Client): The MQTT client instance.
        command_callback (callable): A callback function to handle incoming commands.

    """

    def __init__(self, broker_name: str, command_callback=None) -> None:
        """
        Initializes an MQTTClient object.

        Args:
            broker_name (str): The name of the MQTT broker.
            command_callback (callable, optional): A callback function to handle incoming commands.

        """
        self.broker_name: str = broker_name
        self.client = mqtt.Client("jaa369_d3_RPi")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_name, keepalive=60)
        self.command_callback = command_callback

    def on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        """
        Callback function called when the MQTT client is connected to the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (object): User-defined data.
            flags (dict): Response flags sent by the broker.
            rc (int): The connection result code.

        """
        self.client.subscribe("jaa369/parking/displayBoard/")
        self.client.subscribe("jaa369/parking/system/")

    def on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        """
        Callback function called when a new MQTT message is received.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (object): User-defined data.
            msg (mqtt.MQTTMessage): The received MQTT message.

        """
        logging.info(f"Received `{msg.payload}` from topic `{msg.topic}`")
        payload = json.loads(msg.payload)
        if msg.topic == "jaa369/parking/displayBoard/":
            print(self.format_displayBoard(payload))
        elif msg.topic == "jaa369/parking/system/":
            if 'command' in payload and self.command_callback:
                self.command_callback(payload['command'])

    def format_displayBoard(self, payload: json) -> str:
        """
        Formats the display board payload.

        Args:
            payload (json): The display board payload.

        Returns:
            str: The formatted display board message.

        """
        return f"{payload['message']} - {payload['timestamp']}"

    def start(self) -> None:
        """
        Starts the MQTT client's event loop.

        """
        self.client.loop_start()

    def stop(self) -> None:
        """
        Stops the MQTT client's event loop.

        """
        self.client.loop_stop()

    def publish(self, topic: str, payload: json) -> None:
        """
        Publishes a message to the specified MQTT topic.

        Args:
            topic (str): The MQTT topic to publish to.
            payload (json): The payload of the message.

        """
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
    """
    Represents an edge node in a parking system.

    Attributes:
        light_pins (Tuple[int]): The GPIO pins for the warning lights.
        adcAddr (int): The address of the ADC sensor.
        broker (str): The MQTT broker address.

    Methods:
        __init__(self, light_pins: Tuple[int], adcAddr: int, broker: str) -> None:
            Initializes the EdgeNode object.
        handle_new_command(self, new_command: str) -> None:
            Handles a new command received from the MQTT client.
        serverSide(self) -> None:
            Runs the server side of the application.
        clientSide(self) -> None:
            Runs the client side of the application.
        run(self) -> None:
            Runs the edge node.
        getInput(self) -> int:
            Gets the input from the user.
        readSensorAndPublish(self) -> None:
            Reads the sensor data and publishes it to the MQTT topics.
    """
    def __init__(self, light_pins: Tuple[int], adcAddr: int, broker: str) -> None:
        self.dataSensor = ADCSensor(adcAddr)
        self.lights = WarningLight(light_pins)
        self.command_lock = threading.Lock()
        self.running = True  # Control execution of threads
        self.mqtt_client = MQTTClient(broker, command_callback=self.handle_new_command)
        self.parkingSpot = ParkingSpot()
        self.RGB_RED: int = light_pins[0]
        self.RGB_GREEN: int = light_pins[1]
        self.RGB_BLUE: int = light_pins[2]
        self.command = None

        # Threads
        # Two threads to run the server and client side of the application
        self.server_thread = threading.Thread(target=self.serverSide)
        self.client_thread = threading.Thread(target=self.clientSide)

    def handle_new_command(self, new_command: str) -> None:
        """
        Handles a new command received from the MQTT client.

        Args:
            new_command (str): The new command received.
        """
        with self.command_lock:
            self.command = new_command

    def serverSide(self) -> None:
        """
        Runs the server side of the application.
        """
        while self.running:
            if self.parkingSpot.isFull():
                logging.warning("Parking lot is full")
            try:
                spot = self.getInput()
            except ValueError:
                logging.error("Invalid input")
                continue
            except KeyboardInterrupt:
                logging.info("Exiting App: User pressed Ctrl+C...")
                sys.exit(0)
            time.sleep(1)

    def clientSide(self) -> None:
        """
        Runs the client side of the application.
        Deals with displaying contents of the MQTT command messages for the 
        emergency lights from the QT side of the application to the console.
        """
        while self.running:
            with self.command_lock:
                if self.command == "WARN ON":
                    self.lights.startFlash(self.RGB_RED)
                elif self.command == "WARN OFF":
                    self.lights.stopFlash()
                self.command = None
            time.sleep(1)

    def run(self) -> None:
        """
        Runs the edge node.
        """
        self.mqtt_client.start()
        self.server_thread.start()
        self.client_thread.start()
        try:
            while self.running:
                # Main thread can continue to run or wait
                # for other threads to finish
                time.sleep(1)

        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Exiting App...")
            self.running = False  # Stop the threads
            self.lights.stopFlash()
            self.commmand_lock.release()  # Release the lock
            GPIO.cleanup()
            self.server_thread.join()
            self.client_thread.join()
            self.mqtt_client.stop()
            logging.info("Exiting App...")

    def getInput(self) -> int:
        """
        Gets the input from the user.

        Returns:
            int: The input received from the user.
        """
        # Get the input from the user
        print("0: Spot 1\n")
        print("1: Spot 2\n")
        print("2: Spot 3\n")
        print("3: Spot 4\n")
        print("4: Spot 5\n")
        print("5: Clear a spot\n")
        print("6: Exit\n")
        print("Enter the command: \n")
        spot = int(input())
        if spot == 5:
            print("Enter the parking spot number to clear: \n")
            spot = int(input())
            self.parkingSpot.clear(spot)
            logging.info("Uploading data and parking spot status to the cloud")
            self.readSensorAndPublish()
        elif spot == 6:
            raise KeyboardInterrupt
        else:
            assert spot >= 0 and spot <= 4
            self.parkingSpot.update(spot)
            logging.info("Uploading data and parking spot status to the cloud")
            self.readSensorAndPublish()
        return spot

    def readSensorAndPublish(self) -> None:
        """
        Reads the sensor data and publishes it to the MQTT topics.
        """
        parking_payload = {
            "message": "From RPi: Parking lot status",
            "sensorValue": self.dataSensor.read(),
            "parkingLotData": self.parkingSpot.spots,
            "occupiedSlots": self.parkingSpot.occupied,
            "isFull": self.parkingSpot.isFull(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " CST"
        }
        self.mqtt_client.publish("jaa369/parking/system/", json.dumps(parking_payload))
        self.mqtt_client.publish("jaa369/parking/displayBoard/", json.dumps(parking_payload))

        

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