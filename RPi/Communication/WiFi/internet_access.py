import json
import io
import os

MAP_URL = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?Building={building}&Level={level}"
STATUS_OK = 200


def get_floor_plan(building, level):
    """
    function to download the floor plan
    :param building:
    :param level:
    :return floor representaion:
    """
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/' + building + '_' + level + '.json'
    with io.open(filepath, 'r') as data_file:
        plan = json.load(data_file)
    return plan


if __name__ == '__main__':
    print get_floor_plan('COM2', '3')
