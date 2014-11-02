from Navigation.navigation import Navigation
from Navigation.map import Map
from datetime import datetime
from time import mktime
from Communication.Uart.uart_communication import receive_data, initiate_connection, check_connection_status
from Speech.espeak_api import VoiceOutput
from Speech.voice_recognition import VoiceRecognition
from ObstacleDetection.ultrasonic_data import UltrasonicData
from Communication.WiFi.ping_internet import is_connected
from local_logger import get_local_logger

FASTER_LOOP_TIMER = 2
SLOWER_LOOP_TIMER = 10

is_running_mode = True

ultrasonic_handle = UltrasonicData()
voice_output = VoiceOutput()
user_input = VoiceRecognition()
logger = get_local_logger()

REACH_END = UltrasonicData.TURN_BACK + 1

command_table = {
    UltrasonicData.TURN_STRAIGHT: 'keep straight',
    UltrasonicData.TURN_LEFT: 'turn left',
    UltrasonicData.TURN_LEFT_SLIGHTLY: 'turn left slightly',
    UltrasonicData.TURN_RIGHT: 'turn right',
    UltrasonicData.TURN_RIGHT_SLIGHTLY: 'turn right slightly',
    UltrasonicData.TURN_BACK: 'move backwards please',
    REACH_END: 'you have reached your destination'
}


def now():  # return seconds since epoch
    dt = datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond / 1000000.0


def remap_direction(rawDir):
    return int(rawDir) * 2


def remap_distance(rawDist):
    return float(rawDist)


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
        user_commands = user_input.get_command()
        if user_commands is not None:
            commands = user_commands.split(' ')
            for cmd in commands:
                intepreted_command = command_lookup.get(cmd.strip(), None)
                if intepreted_command is not None and type(intepreted_command) is int:
                    accumulated_input = accumulated_input * 10 + intepreted_command
        else:
            voice_output.speak('input is not valid. please try again')
            continue
        voice_output.speak('input is {0}'.format(user_commands.strip().lower()))
        voice_output.speak('confirm or cancel the input')
        final_cmd = user_input.get_command()
        is_input_done = command_lookup.get(final_cmd.strip(), False)
        if type(is_input_done) is bool and is_input_done:
            voice_output.speak('input {0} is confirmed'.format(user_commands.strip().lower()))
        else:
            is_input_done = False
            voice_output.speak('please redo the input')
    return str(accumulated_input)


def get_user_input():
    building = 'COM1'
    level = '2'
    start = '32'
    end = '11'
    voice_output.speak('please input current building')
    building = get_input()
    print building
    voice_output.speak('please input current level')
    level = get_input()
    has_asked_current_question = False
    while True:
        if has_asked_current_question:
            voice_output.speak('sorry, cannot find given position. please input current position again')
        else:
            voice_output.speak('please input current position')
        start = get_input()
        has_asked_current_question = True
        if Map.get_node_by_location_id(building, level, start):
            break
    has_asked_current_question = False
    while True:
        if has_asked_current_question:
            voice_output.speak('sorry, cannot find given position. please input your destination again')
        else:
            voice_output.speak('please input your destination')
        end = get_input()
        has_asked_current_question = True
        if Map.get_node_by_location_id(building, level, end):
            break
    return building, level, start, end


def run():
    voice_output.speak('welcome to navicane system')
    (building, level, start, end) = get_user_input()
    voice_output.speak('You are going to building {0} level {1} from {2} to {3}'.format(building, level,
                                                                                        start, end))
    startPtName = Map.get_node_by_location_id(building, level, start)['nodeName']
    endPtName = Map.get_node_by_location_id(building, level, end)['nodeName']
    nav = Navigation(building, level, startPtName, endPtName)
    if is_connected():
        voice_output.speak('downloaded the map from internet. ready to navigate')
    else:
        voice_output.speak('the internet is not available. use default map instead')

    # at the beginning, say the nav instruction first
    is_data_corrupted, sensors_data = receive_data()
    if not is_data_corrupted:
        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))  # next loc's ID
        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))  # next loc's direction

    faster_loop_time = now()
    runner = 0
    global is_running_mode
    while is_running_mode:
        while not check_connection_status():
            # voice_output.speak('set up connection')
            initiate_connection()
        if now() - faster_loop_time > FASTER_LOOP_TIMER:
            is_data_corrupted, sensors_data = receive_data()
            if not is_data_corrupted:
                logger.info('front right: {0}; front left: {1};right: {2};left: {3}'.format(str(sensors_data[0]),
                                                                                            str(sensors_data[1]),
                                                                                            str(sensors_data[2]),
                                                                                            str(sensors_data[3])))
                logger.info('compass: {0}; barometer: {1};distance: {2}'.format(str(sensors_data[4]),
                                                                                str(sensors_data[5]),
                                                                                str(sensors_data[6])))
                ultrasonic_handle.feed_data(sensors_data[1], sensors_data[0],
                                            sensors_data[3], sensors_data[2])
                nav.update_pos_by_dist_and_dir(remap_distance(sensors_data[6]), remap_direction(sensors_data[4]))
                print "current pos is"  # TODO: remove this after eval 2 drill
                print nav.get_pos()  # TODO: remove this after eval 2 drill
                print "next location pos is"  # TODO: remove this after eval 2 drill
                print "[" + nav.nextLoc["x"] + ", " + nav.nextLoc["y"] + "]"  # TODO: remove this after eval 2 drill
                if runner == 0:
                    if nav.is_reach_next_location():
                        voice_output.speak('you just reached {0}'.format(str(nav.nextLoc["nodeId"])))
                        if not nav.is_reach_end():
                            give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))
                        else:
                            give_current_instruction(REACH_END)
                            is_running_mode = False
                    else:
                        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))
                else:
                    if nav.is_reach_next_location():
                        voice_output.speak('you just reached {0}'.format(str(nav.nextLoc["nodeId"])))
                        if not nav.is_reach_end():
                            give_current_instruction()
                        else:
                            give_current_instruction(REACH_END)
                            is_running_mode = False
                    else:
                        give_current_instruction()
            runner = (runner + 1) % 5
            faster_loop_time = now()


if __name__ == '__main__':
    global is_running_mode
    is_running_mode = True
    while True:
        run()
        is_running_mode = True
