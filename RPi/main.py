from datetime import datetime
from time import mktime
import multiprocessing
from Navigation.guidance import Guidance
from Navigation.special_node import SpecialNode
from Navigation.map import Map
from Communication.Uart.uart_communication import receive_data, initiate_connection, check_connection_status
from Speech.espeak_api import VoiceOutput
from Speech.voice_recognition import VoiceRecognition
from ObstacleDetection.ultrasonic_data import UltrasonicData
from Positioning.ir_reading import ir_read
from local_logger import get_local_logger

FASTER_LOOP_TIMER = 1

is_running_mode = True

ultrasonic_handle = UltrasonicData()
voice_output = VoiceOutput()
user_input = VoiceRecognition()
logger = get_local_logger()
totalSteps = 0
calibratedNodes = []

REACH_END = UltrasonicData.TURN_BACK + 1

command_table = {
    UltrasonicData.TURN_STRAIGHT: 'keep straight',
    UltrasonicData.TURN_LEFT: 'turn left',
    UltrasonicData.TURN_LEFT_SLIGHTLY: 'turn left slightly',
    UltrasonicData.TURN_RIGHT: 'turn right',
    UltrasonicData.TURN_RIGHT_SLIGHTLY: 'turn right slightly',
    UltrasonicData.TURN_BACK: 'backwards',
    REACH_END: 'you have reached your destination'
}

ir_reading_queue = multiprocessing.Queue()
ir_reading_process = multiprocessing.Process(target=ir_read, args=(ir_reading_queue,))
ir_reading_process.start()


def now():  # return seconds since epoch
    dt = datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond / 1000000.0


def remap_direction(rawDir):
    return (int(rawDir) * 2 + 180) % 360


def remap_distance(steps):
    global totalSteps
    deltaSteps = 0
    if steps >= totalSteps:  # normal case
        deltaSteps = steps - totalSteps
        totalSteps = steps
    else:  # reset already
        deltaSteps = steps + 255 - totalSteps
        totalSteps = steps
    return float(deltaSteps * 88)


def give_current_instruction(status=None):
    # if navigation has something, output navigation
    ultrasonic_status = ultrasonic_handle.get_instruction()
    if status and type(status) is not int:
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
        'CANCEL': False
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
            voice_output.speak('please try again')
            continue
        voice_output.speak('input is {0}'.format(user_commands.strip().lower()))
        voice_output.speak('confirm or cancel the input')
        final_cmd = user_input.get_command()
        is_input_done = command_lookup.get(final_cmd.strip(), False)
        if is_input_done and len(str(accumulated_input)) > 2:
            voice_output.speak('input {0} is confirmed'.format(user_commands.strip().lower()))
        else:
            is_input_done = False
            accumulated_input = 0
            voice_output.speak('please redo the input')
    return str(accumulated_input)


def get_user_input():
    starting_building = 'COM1'
    starting_level = '2'
    starting_point = '26'
    ending_building = 'COM2'
    ending_level = '2'
    ending_point = '14'
    voice_output.speak('start')

    user_input = get_input()
    print user_input
    starting_building = 'COM' + user_input[0]
    starting_level = user_input[1]
    starting_point = user_input[2:]
    voice_output.speak('end')
    user_input = get_input()
    print user_input
    ending_building = 'COM' + user_input[0]
    ending_level = user_input[1]
    ending_point = user_input[2:]

    return starting_building, starting_level, starting_point, ending_building, ending_level, ending_point


def run():
    voice_output.speak('welcome to navicane system')
    (starting_building, starting_level, starting_point,
     ending_building, ending_level, ending_point) = get_user_input()
    # TODO: may get NONE if input param is incorrect, if incorrect should re-input
    # startPtName = Map.get_node_by_location_id(starting_building, starting_level, starting_point)['nodeName']
    # endPtName = Map.get_node_by_location_id(ending_building, ending_level, ending_point)['nodeName']
    nav = Guidance(starting_building, starting_level, starting_point, ending_building, ending_level, ending_point)
    voice_output.speak('start navigation')

    voice_output.speak('set up u art connection')
    while not check_connection_status():
        initiate_connection()
    voice_output.speak('set up ok')
    is_data_corrupted, sensors_data = receive_data()
    if not is_data_corrupted:
        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))  # next loc's ID
        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))  # next loc's direction
        global totalSteps
        totalSteps = int(sensors_data[6])

    faster_loop_time = now()
    runner = 0
    global is_running_mode
    while is_running_mode:
        isJustCalibrated = False
        if not ir_reading_queue.empty():
            state = ir_reading_queue.get(block=False)
        else:
            state = 0
        while not check_connection_status():
            initiate_connection()
        if state == 1:  # special pattern recognized! the actual pos for the special node
            pos = nav.get_pos()
            print '\npattern is 1\n'
            print nav.get_next_loc()
            print nav.get_prev_loc()
            if SpecialNode.is_special_node(nav.get_curr_building(), nav.get_curr_level(), nav.get_next_loc()):
                # reach the actual important loc but not reach the point on the map
                if Map.get_distance(pos[0], nav.get_next_loc()['x'], pos[1], nav.get_next_loc()['y']) < 500 and \
                   nav.get_next_loc()['nodeName'] not in calibratedNodes:
                    calibratedNodes.append(nav.get_next_loc()['nodeName'])
                    nav.reach_special_node(nav.get_next_loc())
                    isJustCalibrated = True
            elif SpecialNode.is_special_node(nav.get_curr_building(), nav.get_curr_level(), nav.get_prev_loc()):
                print 'prev is special'
                # reach the actual important loc but map shows passed the node already
                if Map.get_distance(pos[0], nav.get_prev_loc()['x'], pos[1], nav.get_prev_loc()['y']) < 500 and \
                   nav.get_prev_loc()['nodeName'] not in calibratedNodes:
                    print nav.get_prev_loc()['nodeName']
                    calibratedNodes.append(nav.get_prev_loc()['nodeName'])
                    nav.reach_special_node(nav.get_prev_loc())
                    isJustCalibrated = True
        if isJustCalibrated:
            voice_output.speak('calibrated')
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
                deltaDist = remap_distance(sensors_data[6])
                print "delta dist is " + str(deltaDist)
                if not isJustCalibrated:
                    nav.update_pos_by_dist_and_dir(deltaDist, remap_direction(sensors_data[4]))
                print "current pos is"  # TODO: remove this after eval 2 drill
                print nav.get_pos()  # TODO: remove this after eval 2 drill
                print "next location pos is"  # TODO: remove this after eval 2 drill
                print "[" + nav.get_next_loc()["x"] + ", " + nav.get_next_loc()["y"] + "]"
                if runner == 0:
                    if nav.is_reach_next_location():
                        voice_output.speak('you just reached {0}'.format(str(nav.get_next_loc()["nodeId"])))
                        if not nav.is_reach_end():
                            give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))
                        else:
                            give_current_instruction(REACH_END)
                            is_running_mode = False
                    else:
                        give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))
                else:
                    if nav.is_reach_next_location():
                        voice_output.speak('you just reached {0}'.format(str(nav.get_next_loc()["nodeId"])))
                        if not nav.is_reach_end():
                            give_current_instruction(nav.get_next_instruction(remap_direction(sensors_data[4])))
                        else:
                            give_current_instruction(REACH_END)
                            is_running_mode = False
                    else:
                        give_current_instruction()
            runner = (runner + 1) % 2
            faster_loop_time = now()


if __name__ == '__main__':
    global is_running_mode
    is_running_mode = True
    while True:
        run()
        is_running_mode = True
