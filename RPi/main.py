from Navigation.navigation import Navigation
from Communication.Uart.uart_communication import receive_data, initiate_connection
from datetime import datetime
from time import mktime
from Speech import espeak_api

FASTER_LOOP_TIMER = 3
SLOWER_LOOP_TIMER = 10


def now():  # return seconds since epoch
    dt = datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond / 1000000.0


while True:
    """ StandBy Mode """
    building = level = start = end = ""
    while False:
        # handle keypad input here
        # TODO: get_maps, get_levels, get_all_locations
        print "Pseudo keypad input"
        building = "Com1"
        level = "2"
        start = "P2"
        end = "P10"

    nav = Navigation(building, level, start, end)  # pseudo input for start, end pts
    initiate_connection()
    fasterLoopTime = now()
    slowerLoopTime = now()
    sensorsData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """ Navigation Mode """
    while True:
        # while user not presses 'cancel' key
        # faster loop (every 3s):
        if now() - fasterLoopTime > FASTER_LOOP_TIMER:
            print "enter faster loop"

            isDataCorrupted, sensorsData = receive_data()
            if isDataCorrupted == 1:
                print "=============SENSORS==============="
                print "front right ultrasonic sensors(us)"
                print sensorsData[0]
                print "front left ultrasonic sensors(us)"
                print sensorsData[1]
                print "right ultrasonic sensors(us)"
                print sensorsData[2]
                print "left ultrasonic sensors(us)"
                print sensorsData[3]
                print "compass"
                print sensorsData[4]
                print "barometer"
                print sensorsData[5]
                print "distance"
                print sensorsData[6]
                print "==================================="
                # if reach the end ... do something
                # do any calibration ...
                # obstacle avoidance ...

            fasterLoopTime = now()

        if now() - slowerLoopTime > SLOWER_LOOP_TIMER:
            print "enter slower loop"

            # TODO: only get certain sensors data
            isDataCorrupted, sensorsData = receive_data()
            if isDataCorrupted == 1:
                print "=============SENSORS==============="
                print "front right ultrasonic sensors(us)"
                print sensorsData[0]
                print "front left ultrasonic sensors(us)"
                print sensorsData[1]
                print "right ultrasonic sensors(us)"
                print sensorsData[2]
                print "left ultrasonic sensors(us)"
                print sensorsData[3]
                print "compass"
                print sensorsData[4]
                print "barometer"
                print sensorsData[5]
                print "distance"
                print sensorsData[6]
                print "==================================="

            print nav.get_next_location_details(sensorsData[4], 0, 0)

            slowerLoopTime = now()
