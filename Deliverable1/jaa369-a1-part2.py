# Jesse Aguirre
# CME466: Intro to Raspberry Pi P2
# 2024-01-11

import RPi.GPIO as GPIO
import time
import PCF8591 as ADC

# Constants
PINS = (17, 18, 27, 25)  # Blue, Green, Red, Switch
RGB_B, RGB_G, RGB_R, SWITCH = PINS
ADC_ADDRESS = 0x48
VOICE_THRESHOLD = 80
VOICE_MIDDLE = 120

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
    if voice_val < VOICE_THRESHOLD:
        print("Too Loud!")
        set_led_color(False, False, True)  # Yellow
    elif VOICE_THRESHOLD <= voice_val < VOICE_MIDDLE:
        print("Just Right!")
        set_led_color(False, True, False)  # Purple
    else:
        print("Dead Quiet!")
        set_led_color(True, False, False)  # Blue

def set_led_color(red, green, blue):
    GPIO.output(RGB_R, GPIO.LOW if red else GPIO.HIGH)
    GPIO.output(RGB_G, GPIO.LOW if green else GPIO.HIGH)
    GPIO.output(RGB_B, GPIO.LOW if blue else GPIO.HIGH)

def loop():
    global voice_enabled
    voice_enabled = False
    while True:
        if voice_enabled:
            voice_val = ADC.read(0)
            print(f"Voice val is: {voice_val}")
            update_leds(voice_val)
            time.sleep(0.2)

def destroy():
    for pin in PINS[:-1]:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
