from Navigation.navigation import Navigation
from Communication.Uart.uart_communication import receive_data, initiate_connection, check_connection_status
from datetime import datetime
from time import mktime
from Speech.espeak_api import VoiceOutput
from ObstacleDetection.ultrasonic_data import UltrasonicData

FASTER_LOOP_TIMER = 3
SLOWER_LOOP_TIMER = 10

ultrasonic_handle = UltrasonicData()
voice_output = VoiceOutput()

command_table = {
    UltrasonicData.TURN_STRAIGHT: 'keep straight',
    UltrasonicData.TURN_LEFT: 'turn left',
    UltrasonicData.TURN_LEFT_SLIGHTLY: 'turn left slightly',
    UltrasonicData.TURN_RIGHT: 'turn right',
    UltrasonicData.TURN_RIGHT_SLIGHTLY: 'turn right slightly',
    UltrasonicData.TURN_LEFT_AND_RIGHT: 'turn left or right',
    UltrasonicData.TURN_BACK: 'turn back please'
}


def now():  # return seconds since epoch
    dt = datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond / 1000000.0


def give_current_instruction():
    # if navigation has something, output navigation
    ultrasonic_status = ultrasonic_handle.get_instruction()
    current_command = command_table[ultrasonic_status]
    voice_output.speak(current_command)


while True:
    """ StandBy Mode """
    building = level = start = end = ""
    print "Pseudo keypad input"
    building = "COM1"
    level = "2"
    start = "P2"
    end = "P10"

    nav = Navigation(building, level, start, end)
    while not check_connection_status():
        initiate_connection()
    fasterLoopTime = now()
    slowerLoopTime = now()
    sensorsData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """ Navigation Mode """
    while True:
        while not check_connection_status():
            print 'connection lost, re-establishing'
            initiate_connection()
        # while user not presses 'cancel' key
        # faster loop (every 3s):
        if now() - fasterLoopTime > FASTER_LOOP_TIMER:
            print "enter faster loop"

            isDataCorrupted, sensorsData = receive_data()
            if not isDataCorrupted:
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
                ultrasonic_handle.feed_data(sensorsData[1], sensorsData[0],
                                            sensorsData[2], sensorsData[3])
                # TODO: get deltaX and deltaY from sensors
                deltaX = 0
                deltaY = 0
                newPos = nav.update_pos(deltaX, deltaY)

                if nav.is_reach_next_location():
                    if not nav.is_reach_end():
                        nav.get_next_location_by_direction(sensorsData[4])
                    else:
                        print "reach the end!"

            fasterLoopTime = now()

        if now() - slowerLoopTime > SLOWER_LOOP_TIMER:
            print "enter slower loop"

            # TODO: only get certain sensors data
            isDataCorrupted, sensorsData = receive_data()
            if not isDataCorrupted:
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

                if nav.is_reach_next_location():
                    if not nav.is_reach_end():
                        nav.get_next_location_by_direction(sensorsData[4])
                    else:
                        print "reach the end!"
                else:
                    nav.get_next_location_by_direction(sensorsData[4])

            slowerLoopTime = now()
