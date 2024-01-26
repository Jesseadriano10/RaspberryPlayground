import RPi.GPIO as GPIO
import PCF8591 as ADC
import time 
import math
import paho.mqtt.client as mqtt

broker = "broker.hivemq.com"
client = mqtt.Client("jaa369_raspi")
client.connect(broker)

BtnPin = 25   
Rpin = 27    
Gpin = 18    
Bpin = 17 

def setUp():
    GPIO.setmode(GPIO.BCM)
    ADC.setup(0x48)
    GPIO.setwarnings(False)

    # Switch Trigger
    GPIO.setup(BtnPin, GPIO.IN)
    GPIO.setup(Tmp_pin, GPIO.IN)

    # LED Trigger
    GPIO.setup(Rpin, GPIO.OUT)
    GPIO.setup(Gpin, GPIO.OUT)
    GPIO.setup(Bpin, GPIO.OUT)

def Led(r, g, b):
    GPIO.output(Rpin, r)
    GPIO.output(Gpin, g)
    GPIO.output(Bpin, b)


def readSensor():
    AnalogVal = ADC.read(0)
    return AnalogVal

def destroy():
    GPIO.output(Gpin, GPIO.HIGH)
    GPIO.output(Rpin, GPIO.HIGH)
    GPIO.cleanup()

def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    r = False
    g = False
    b = False
    if (msg[0] == "0"):
        r = True
    if (msg[1] == "0"):
        g = True
    if (msg[2] == "0"):
        b = True
    Led(r,g,b)
    print("r g b")

def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    if (msg == "ledOn"):
        Led(False, False, False)
        print("LED turning on...")
    elif (msg == "ledRed"):
        Led(False, True, True)
        print("LED turning red on...")
    elif (msg == "ledGreen"):
        Led(True, False, True)
        print("LED turning green on...")
    elif (msg == "ledBlue"):
        Led(True, True, False)
        print("LED turning blue on...")
    elif (msg == "readSen"):
        print("Reading from the sensor..")
        temp = readSensor()
        print("Temperature read:", round(temp, 2), "C")

# Program Start
if __name__ == '__main__':
    setUp()
    Led(False, False, False)
    try:
        client.loop_start()
        client.subscribe("jaa369_read")
        client.on_message = on_message
        time.sleep(100)
    except KeyboardInterrupt:
        destroy()
    
