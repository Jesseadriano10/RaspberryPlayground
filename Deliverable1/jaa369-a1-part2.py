# Jesse Aguirre
# CME466: Intro to Raspberry Pi P2
# 2024-01-11

import RPi.GPIO as GPIO
import time
import PCF8591 as ADC

pins = (17, 18, 27, 25) # Blue, Green, Red, Switch
rgb_B = pins[0]
rgb_G = pins[1]
rgb_R = pins[2]
switch = pins[3]
colors = (rgb_B, rgb_G, rgb_R)
def setup(pins):
    GPIO.setmode(GPIO.BCM) # Numbers GPIOs by physical location
    # LED CONFIG
    for i in range(len(pins)-1):
        print("Configuring pin: " + str(pins[i]))
        GPIO.setup(pins[i], GPIO.OUT) # Set all LED pins mode as output
    # SWITCH CONFIG
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set button pin mode as input pull-up to HIGH level(3.3V)
    GPIO.add_event_detect(switch, GPIO.BOTH, callback=detect) # wait for falling
    # Configure PCF8591 ADC
    print("Configuring ADC")
    ADC.setup(0x48)
def detect(chn):
    Led(GPIO.input(switch))

def loop():
    global voice_enabled
    voice_enabled = False
    while True:
        if voice_enabled:
            voice_val = ADC.read(0)
            if voice_val:
                print("Voice val is: ", voice_val)
                if voice_val < 80:
                    print("Too Loud!")
                    # Turn Yellow
                    GPIO.output(rgb_R, GPIO.LOW)
                    GPIO.output(rgb_G, GPIO.LOW)
                    GPIO.output(rgb_B, GPIO.HIGH)
                elif voice_val < 120 and voice_val > 80:
                    print("Just Right!")
                    # Turn Purple
                    GPIO.output(rgb_R, GPIO.LOW)
                    GPIO.output(rgb_G, GPIO.HIGH)
                    GPIO.output(rgb_B, GPIO.LOW)
                else:
                    print("Dead Quiet!")
                    # Turn Blue
                    GPIO.output(rgb_R, GPIO.HIGH)
                    GPIO.output(rgb_G, GPIO.LOW)
                    GPIO.output(rgb_B, GPIO.LOW)
                time.sleep(0.2)
        
        
        


def destroy():
    for i in range(len(pins) - 1):
        GPIO.output(pins[i], GPIO.LOW) # Turn off all LEDs
    
    GPIO.cleanup() # Release resource

# Each time the button is pressed, the LED will change color based on list
def Led(x):
    global voice_enabled
    if x == 0:
        # Whenever the button is pressed, we will allow voice detection
        voice_enabled = True
    else:
        voice_enabled = False
        print("Press the button to enable voice detection!")
        # Turn LED Red
        GPIO.output(rgb_R, GPIO.LOW)
        GPIO.output(rgb_G, GPIO.HIGH)
        GPIO.output(rgb_B, GPIO.HIGH)
    

    
if __name__ == '__main__': # Program starts from here
    setup(pins)
    try:
        loop()
    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        destroy()