class UltrasonicData(object):
    FRONT_LEFT_DATA_KEY = 'front_left'
    FRONT_RIGHT_DATA_KEY = 'front_right'
    LEFT_DATA_KEY = 'left'
    RIGHT_DATA_KEY = 'right'
    BUFFER_SIZE = 2
    TURN_LEFT = 'turn left'
    TURN_LEFT_SLIGHTLY = 'turn left slightly'
    TURN_RIGHT = 'turn right'
    TURN_RIGHT_SLIGHTLY = 'turn right slightly'
    KEEP_STRAIGHT = 'keep straight'

    def __init__(self, safe_limit):
        super(UltrasonicData, self).__init__()
        self._safe_limit = safe_limit
        self._sensor_data = {}
        self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.LEFT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.RIGHT_DATA_KEY] = []

    def feed_data(self, front_left, front_right, left, right):
        def get_average(ls):
            result = 0
            for item in ls:
                result += item
            return (result * 0.1) / len(ls)

        def get_instruction(front_left_average, front_right_average, left_average, right_average):
            if front_left_average < self._safe_limit and front_right_average < self._safe_limit:
                if left_average > right_average and left_average > self._safe_limit:
                    return UltrasonicData.TURN_LEFT
                elif right_average > left_average and right_average > self._safe_limit:
                    return UltrasonicData.TURN_RIGHT
                else:
                    raise Exception('Dude, dead end, turn back')
            elif front_left_average < self._safe_limit:
                return UltrasonicData.TURN_RIGHT_SLIGHTLY
            elif front_right_average < self._safe_limit:
                return UltrasonicData.TURN_RIGHT_SLIGHTLY
            else:
                return UltrasonicData.KEEP_STRAIGHT

        self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY].append(front_left)
        self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY].append(front_right)
        self._sensor_data[UltrasonicData.LEFT_DATA_KEY].append(left)
        self._sensor_data[UltrasonicData.RIGHT_DATA_KEY].append(right)
        if len(self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY]) > UltrasonicData.BUFFER_SIZE:
            self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.LEFT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.RIGHT_DATA_KEY].pop(0)
        front_left_average = get_average(self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY])
        front_right_average = get_average(self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY])
        left_average = get_average(self._sensor_data[UltrasonicData.LEFT_DATA_KEY])
        right_average = get_average(self._sensor_data[UltrasonicData.RIGHT_DATA_KEY])
        return get_instruction(front_left_average, front_right_average, left_average, right_average)
