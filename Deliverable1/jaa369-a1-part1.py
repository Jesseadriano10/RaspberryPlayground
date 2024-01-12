# Jesse Aguirre
# CME466: Intro to Raspberry Pi P1
# 2024-01-11

import RPi.GPIO as GPIO
import time
import random

pins = (17, 18, 27, 25) # Blue, Green, Red, Switch
rgb_B = 17
rgb_G = 18
rgb_R = 27
switch = 25
colors = (rgb_B, rgb_G, rgb_R)
def setup(pins):
    GPIO.setmode(GPIO.BCM) # Numbers GPIOs by physical location
    for i in range(len(pins)-1):
        print("Configuring pin: " + str(pins[i]))
        GPIO.setup(pins[i], GPIO.OUT) # Set all LED pins mode as output
    GPIO.setup(pins[3], GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set button pin mode as input pull-up to HIGH level(3.3V)
    GPIO.add_event_detect(pins[3], GPIO.BOTH, callback=detect, bouncetime=200) # wait for falling

def detect(chn):
    Led(GPIO.input(pins[3]))

def loop():
    while True:
        pass


def destroy():
    for i in range(len(pins) - 1):
        GPIO.output(pins[i], GPIO.LOW) # Turn off all LEDs
    GPIO.cleanup() # Release resource

# Each time the button is pressed, the LED will change color based on list
def Led(x):
    if x == 0:
        # Randomize an index between 0-2 to determine which color to turn on/off
        rand = random.randint(0,2)
        if GPIO.input(colors[rand]) == GPIO.LOW:
            GPIO.output(colors[rand], GPIO.HIGH)
        else:
            GPIO.output(colors[rand], GPIO.LOW)
    else:
        print("Push me again to change color")
    

    
if __name__ == '__main__': # Program starts from here
    setup(pins)
    try:
        loop()
    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        destroy()