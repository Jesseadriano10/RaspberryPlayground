# Jesse Aguirre
# CME466: Deliverable 2 Part 3
# 2024-01-25

# Constants for RPI
import RPi.GPIO as GPIO
import time
import PCF8591 as ADC
import sys

# Broker
import paho.mqtt.client as mqtt
import json
from cryptography.fernet import Fernet

# NODE VARIABLES
PINS = (17, 18, 27, 25)  # Blue, Green, Red, Switch
RGB_B, RGB_G, RGB_R, SWITCH = PINS
ADC_ADDRESS = 0x48
VOICE_THRESHOLD = 80
VOICE_MIDDLE = 120
VOLUME_STATUS = ""

# MQTT functions
def connect_mqtt():
    client = mqtt.Client("jaa369_d2publish")
    client.on_connect = on_connect
    client.connect(broker_name, keepalive=60)
    return client

def publish(client):
    global payload
    client.publish("jaa369_sensorData", payload, qos = 0, retain = False)
    print(f"Published `{payload}` to topic `jaa369_sensorData`")
    time.sleep(0.2)

def on_connect(client, userdata, flags, rc):
    if str(rc) == "0" and client.is_connected():
        print(f"Connected to {broker_name} with result code {str(rc)}")
    else:
        print(f"Connection to {broker_name} failed with result code {str(rc)}")



def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in PINS[:-1]:
        print(f"Configuring pin: {pin}")
        GPIO.setup(pin, GPIO.OUT)
    
    GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SWITCH, GPIO.BOTH, callback=button_pressed)
    
    print("Configuring ADC")
    ADC.setup(ADC_ADDRESS)

def button_pressed(channel):
    global voice_enabled
    voice_enabled = GPIO.input(SWITCH)

def update_leds(voice_val):
    global VOLUME_STATUS
    if voice_val < VOICE_THRESHOLD:
        VOLUME_STATUS = "Too Loud!"
        set_led_color(False, False, True)  # Yellow
    elif VOICE_THRESHOLD <= voice_val < VOICE_MIDDLE:
        VOLUME_STATUS = "Just Right!"
        set_led_color(False, True, False)  # Purple
    else:
        VOLUME_STATUS = "Dead Quiet!"
        set_led_color(True, False, False)  # Blue

def set_led_color(red, green, blue):
    GPIO.output(RGB_R, GPIO.LOW if red else GPIO.HIGH)
    GPIO.output(RGB_G, GPIO.LOW if green else GPIO.HIGH)
    GPIO.output(RGB_B, GPIO.LOW if blue else GPIO.HIGH)

# def loop():
#     global voice_enabled
#     global payload
#     voice_enabled = False
#     while True:
#         if voice_enabled:
#             voice_val = ADC.read(0)
#             print(f"Voice val is: {voice_val}")
#             # Package the value of the sensor as a JSON object along with
#             # volume status and timestamp

#             payload = json.dumps({"voice_val": voice_val,
#                                     "volume_status": VOLUME_STATUS,
#                                     "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
            
#             update_leds(voice_val)
#             publish(client)

def destroy():
    for pin in PINS[:-1]:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    global broker_name
    broker_name = sys.argv[1]
    global client
    # RPI
    global voice_enabled
    global payload
    voice_enabled = False
    try:
        client = connect_mqtt()   
        client.loop_start()
        time.sleep(1)
        if client.is_connected():
            print(f"Connected to {broker_name}")
            while True:
                if voice_enabled:
                    voice_val = ADC.read(0)
                    print(f"Voice val is: {voice_val}")
                    # Package the value of the sensor as a JSON object along with
                    # volume status and timestamp

                    payload = json.dumps({"voice_val": voice_val,
                                            "volume_status": VOLUME_STATUS,
                                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                    
                    update_leds(voice_val)
                    publish(client)
        else:
            print(f"Connection to {broker_name} failed")
            client.loop_stop()
            exit()    
    except KeyboardInterrupt:
        destroy()
