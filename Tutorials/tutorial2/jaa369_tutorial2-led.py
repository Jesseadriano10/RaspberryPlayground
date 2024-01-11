import Rpi.GPIO as GPIO
import time

# Set hexadecimal values for each color
# 0xFF00 = red
# 0x00FF = green
# 0x0FF0 = blue
# 0xF00F = purple
# 0x0000 = off
colors = [0xFF00, 0x00FF, 0x0FF0, 0xF00F, 0x0000]
# Pins 17, 18, 21 are connected to RGB led, 21 is a switch
pins = (17, 18, 21, 27)

def setup(pins):
    GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
    GPIO.setup(pins[0:2], GPIO.OUT) # Set all LED pins mode as output
    GPIO.output(pins[0:2], GPIO.LOW) # Set all pins to LOW(0v) to turn off LEDs
    GPIO.setup(pins[3], GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set button pin mode as input pull-up to HIGH level(3.3V)
    GPIO.add_event_detect(pins[3], GPIO.FALLING, callback=loop, bouncetime=200) # wait for falling

def detect(chn):
    print('Button pressed')
    Led(GPIO.input(pins[3]))

# Each time the button is pressed, the LED will change color based on list
def Led(x):
    for i in range(len(colors)):
        GPIO.output(pins[0], (colors[i]&0xFF0000)>>16)
        GPIO.output(pins[1], (colors[i]&0x00FF00)>>8)
        time.sleep(0.5)
    GPIO.output(pins[0:2], GPIO.LOW)
    


def loop():
    setup(pins)