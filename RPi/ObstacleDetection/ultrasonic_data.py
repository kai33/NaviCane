class UltrasonicData(object):
    FRONT_LEFT_DATA_KEY = 'front_left'
    FRONT_RIGHT_DATA_KEY = 'front_right'
    LEFT_DATA_KEY = 'left'
    RIGHT_DATA_KEY = 'right'
    BUFFER_SIZE = 5
    TURN_STRAIGHT = 0
    TURN_LEFT = 1
    TURN_LEFT_SLIGHTLY = 2
    TURN_RIGHT = 3
    TURN_RIGHT_SLIGHTLY = 4
    TURN_LEFT_AND_RIGHT = 5
    TURN_BACK = 6

    def __init__(self, safe_limit=30, side_limit=10, turn_threshold=20):
        super(UltrasonicData, self).__init__()
        self._safe_limit = safe_limit
        self._side_limit = side_limit
        self._turn_threshold = turn_threshold
        self._sensor_data = {}
        self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.LEFT_DATA_KEY] = []
        self._sensor_data[UltrasonicData.RIGHT_DATA_KEY] = []
        self._status_code = UltrasonicData.TURN_STRAIGHT

    def feed_data(self, front_left, front_right, left, right):
        def get_sensor_data(ls):
            return ls[len(ls) - 1]

        def get_instruction(front_left_average, front_right_average, left_average, right_average):
            if front_left_average < self._safe_limit and front_right_average < self._safe_limit:
                if left_average > self._turn_threshold and right_average < self._turn_threshold:
                    return UltrasonicData.TURN_LEFT
                elif left_average < self._turn_threshold and right_average > self._turn_threshold:
                    return UltrasonicData.TURN_RIGHT
                elif left_average > self._turn_threshold and right_average > self._turn_threshold:
                    if left_average > right_average:
                        return UltrasonicData.TURN_LEFT
                    else:
                        return UltrasonicData.TURN_RIGHT
                else:
                    return UltrasonicData.TURN_BACK
            elif front_left_average < self._safe_limit or left_average < self._side_limit:
                return UltrasonicData.TURN_RIGHT_SLIGHTLY
            elif front_right_average < self._safe_limit or right_average < self._side_limit:
                return UltrasonicData.TURN_LEFT_SLIGHTLY
            else:
                return UltrasonicData.TURN_STRAIGHT

        self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY].append(front_left)
        self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY].append(front_right)
        self._sensor_data[UltrasonicData.LEFT_DATA_KEY].append(left)
        self._sensor_data[UltrasonicData.RIGHT_DATA_KEY].append(right)
        if len(self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY]) > UltrasonicData.BUFFER_SIZE:
            self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.LEFT_DATA_KEY].pop(0)
            self._sensor_data[UltrasonicData.RIGHT_DATA_KEY].pop(0)
        front_left_average = get_sensor_data(self._sensor_data[UltrasonicData.FRONT_LEFT_DATA_KEY])
        front_right_average = get_sensor_data(self._sensor_data[UltrasonicData.FRONT_RIGHT_DATA_KEY])
        left_average = get_sensor_data(self._sensor_data[UltrasonicData.LEFT_DATA_KEY])
        right_average = get_sensor_data(self._sensor_data[UltrasonicData.RIGHT_DATA_KEY])
        self._status_code = get_instruction(front_left_average,
                                            front_right_average, left_average, right_average)
        return self._status_code

    def get_instruction(self):
        return self._status_code
