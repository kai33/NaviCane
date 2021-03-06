__author__ = 'Roastedbill'

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN)

count_zero = 0
count_one = 0
pattern_detected = 0


def ir_read(q):
    global count_one
    global count_zero
    global pattern_detected
    while True:
        if (GPIO.input(23) == 1):
            count_zero = 0
            count_one += 1
            if (count_one > 12):
                pattern_detected = 0
        else:
            count_zero += 1
            count_one = 0
            if (count_zero > 12):
                if pattern_detected == 0:
                    q.put(1)
                pattern_detected = 1
        time.sleep(0.05)
    GPIO.cleanup()
