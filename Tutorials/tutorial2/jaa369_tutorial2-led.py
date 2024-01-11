import RPi.GPIO as GPIO
import time

# Set hexadecimal values for each color
# 0xFF00 = red
# 0x00FF = green
# 0x0FF0 = blue
# 0xF00F = purple
# 0x0000 = off
colors = [0xFF00, 0x00FF, 0x0FF0, 0xF00F, 0x0000]
# Pins 17, 18, 21 are connected to RGB led, 21 is a switch
pins = (17, 18, 27, 25) # Blue, Green, Red, Switch
rgb_B = 17
rgb_G = 18
rgb_R = 27



def setup(pins):
    GPIO.setmode(GPIO.BCM) # Numbers GPIOs by physical location
    for i in range(len(pins)-1):
        print("Configuring pin: " + str(pins[i]))
        GPIO.setup(pins[i], GPIO.OUT) # Set all LED pins mode as output
        GPIO.output(pins[i], GPIO.HIGH) # Set all LED pins to high(+3.3V) to off led
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
        print("Button pressed")
        for i in range(len(colors)):
            GPIO.output(rgb_R, (colors[i] & 0x1000) >> 12)
            GPIO.output(rgb_G, (colors[i] & 0x0100) >> 8)
            GPIO.output(rgb_B, (colors[i] & 0x0010) >> 4)
            time.sleep(0.5)
    else:
        print("Button released")
        for i in range(len(pins) - 1):
            GPIO.output(pins[i], GPIO.LOW)
        
    

    
if __name__ == '__main__': # Program starts from here
    setup(pins)
    try:
        loop()
    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        destroy()