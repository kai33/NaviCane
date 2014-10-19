from Navigation.navigation import Navigation
from Navigation.map import Map
from datetime import datetime
from time import mktime
from Speech.espeak_api import VoiceOutput
from Speech.voice_recognition import VoiceRecognition
from ObstacleDetection.ultrasonic_data import UltrasonicData
from Communication.WiFi.ping_internet import is_connected

FASTER_LOOP_TIMER = 3
SLOWER_LOOP_TIMER = 10

is_running_mode = False

ultrasonic_handle = UltrasonicData()
voice_output = VoiceOutput()
user_input = VoiceRecognition()

REACH_END = 7

command_table = {
    UltrasonicData.TURN_STRAIGHT: 'keep straight',
    UltrasonicData.TURN_LEFT: 'turn left',
    UltrasonicData.TURN_LEFT_SLIGHTLY: 'turn left slightly',
    UltrasonicData.TURN_RIGHT: 'turn right',
    UltrasonicData.TURN_RIGHT_SLIGHTLY: 'turn right slightly',
    UltrasonicData.TURN_LEFT_AND_RIGHT: 'turn left or right',
    UltrasonicData.TURN_BACK: 'turn back please',
    REACH_END: 'you have reached your destination'
}


def now():  # return seconds since epoch
    dt = datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond / 1000000.0


def give_current_instruction(status=None):
    # if navigation has something, output navigation
    ultrasonic_status = ultrasonic_handle.get_instruction()
    if status and type(status) is str:
        current_command = status
    elif status:
        current_command = command_table[status]
    else:
        current_command = command_table[ultrasonic_status]
    voice_output.speak(current_command)


def get_input():
    command_lookup = {
        'ZERO': 0,
        'ONE': 1,
        'TWO': 2,
        'THREE': 3,
        'FOUR': 4,
        'FIVE': 5,
        'SIX': 6,
        'SEVEN': 7,
        'EIGHT': 8,
        'NINE': 9,
        'CONFIRM': True,
        'CANCEL': False,
        'PREVIOUS': 'previous',
        'NEXT': 'next'
    }
    accumulated_input = 0
    is_input_done = False
    while not is_input_done:
        user_command = user_input.get_command()
        print user_command
        if user_command is not None:
            intepreted_command = command_lookup.get(user_command, None)
        else:
            voice_output.speak('input is not valid. please try again')
            continue
        if intepreted_command is not None and type(intepreted_command) is int:
            accumulated_input = accumulated_input * 10 + intepreted_command
            voice_output.speak('input is {0} so far'.format(str(accumulated_input)))
            voice_output.speak('you can input next digit, confirm input or cancel last digit')
        elif intepreted_command is not None and type(intepreted_command) is bool:
            if intepreted_command:
                is_input_done = True
                voice_output.speak('input {0} is confirmed'.format(str(accumulated_input)))
            else:
                accumulated_input = accumulated_input / 10
                voice_output.speak('input is {0} so far'.format(str(accumulated_input)))
        else:
            voice_output.speak('input is {0} so far'.format(str(accumulated_input)))
            voice_output.speak('you can input next digit, confirm input or cancel last digit')
    return str(accumulated_input)


def get_user_input():
    building = "COM1"
    level = "2"
    start = "1"
    end = "10"
    voice_output.speak('please input current building')
    building = get_input()
    voice_output.speak('please input current level')
    level = get_input()
    voice_output.speak('please input current position')
    start = get_input()
    voice_output.speak('please input your destination')
    end = get_input()
    return building, level, start, end


def run():
    (building, level, start, end) = get_user_input()
    if is_connected():
        voice_output.speak('downloaded the map from internet. ready to navigate')
    else:
        voice_output.speak('the internet is not available. use default map instead')

    startPtName = Map.get_node_by_location_id(building, level, start)['nodeName']
    endPtName = Map.get_node_by_location_id(building, level, end)['nodeName']
    nav = Navigation(building, level, startPtName, endPtName)

    from Communication.Uart.uart_communication import receive_data, initiate_connection, check_connection_status
    while is_running_mode:
        while not check_connection_status():
            initiate_connection()
        faster_loop_time = now()
        slower_loop_time = now()
        if now() - faster_loop_time > FASTER_LOOP_TIMER:
            print "enter faster loop"
            is_data_corrupted, sensors_data = receive_data()
            if not is_data_corrupted:
                print "=============SENSORS==============="
                print "front right ultrasonic sensors(us)"
                print sensors_data[0]
                print "front left ultrasonic sensors(us)"
                print sensors_data[1]
                print "right ultrasonic sensors(us)"
                print sensors_data[2]
                print "left ultrasonic sensors(us)"
                print sensors_data[3]
                print "compass"
                print sensors_data[4]
                print "barometer"
                print sensors_data[5]
                print "distance"
                print sensors_data[6]
                print "==================================="
                # if reach the end ... do something
                # do any calibration ...
                # obstacle avoidance ...
                ultrasonic_handle.feed_data(sensors_data[1], sensors_data[0],
                                            sensors_data[2], sensors_data[3])
                # TODO: update user position based on sensor data
                if nav.is_reach_next_location():
                    give_current_instruction("you just reached " + nav.nextLoc["nodeId"])
                    if not nav.is_reach_end():
                        give_current_instruction()
                    else:
                        give_current_instruction(REACH_END)
            faster_loop_time = now()
        if now() - slower_loop_time > SLOWER_LOOP_TIMER:
            print "enter slower loop"
            # TODO: only get certain sensors data
            is_data_corrupted, sensors_data = receive_data()
            if not is_data_corrupted:
                print "=============SENSORS==============="
                print "front right ultrasonic sensors(us)"
                print sensors_data[0]
                print "front left ultrasonic sensors(us)"
                print sensors_data[1]
                print "right ultrasonic sensors(us)"
                print sensors_data[2]
                print "left ultrasonic sensors(us)"
                print sensors_data[3]
                print "compass"
                print sensors_data[4]
                print "barometer"
                print sensors_data[5]
                print "distance"
                print sensors_data[6]
                print "==================================="
                if nav.is_reach_next_location():
                    give_current_instruction("you just reached " + nav.nextLoc["nodeId"])
                    if not nav.is_reach_end():
                        give_current_instruction(nav.get_next_instruction(sensors_data[4]))
                    else:
                        give_current_instruction(REACH_END)
                else:
                    give_current_instruction(nav.get_next_instruction(sensors_data[4]))
            slower_loop_time = now()


if __name__ == '__main__':
    run()
