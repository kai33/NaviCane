class UltrasonicData(object):
    FRONT_LEFT_DATA_KEY = 'front_left'
    FRONT_RIGHT_DATA_KEY = 'front_right'
    LEFT_DATA_KEY = 'left'
    RIGHT_DATA_KEY = 'right'
    BUFFER_SIZE = 2

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
            return None

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
