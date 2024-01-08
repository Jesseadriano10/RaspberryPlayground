import RPi.GPIO as GPIO
import time 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(12, GPIO.OUT)

while True:
    GPIO.output(12, True)
    time.sleep(1)
    GPIO.output(12, False)
    time.sleep(1)
    a = GPIO.input(11)
    print(a)