__author__ = 'Roastedbill'

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(7, GPIO.IN)

count_zero = 0
count_one = 0
is_black = 0
pattern_detected = 0

def ir_read():
    while True:

        if (GPIO.input(7) == 1):
            count_one = 0
            is_black = 1
            count_zero += 1
            if (count_zero > 20):
                pattern_detected = 1

        else:
            count_zero = 0
            count_one += 1
            is_black = 0
            if (count_one > 20):
                pattern_detected = 0

GPIO.cleanup()