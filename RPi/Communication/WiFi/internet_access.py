import urllib2
import json
import io
import os
from ping_internet import is_connected

MAP_URL = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?Building={building}&Level={level}"
STATUS_OK = 200


def get_floor_plan(building, level):
    """
    function to download the floor plan
    :param building:
    :param level:
    :return floor representaion:
    """
    if is_connected():
        url = MAP_URL.format(building=building, level=level)
        response = urllib2.urlopen(url)
        if response.getcode() != STATUS_OK:
            return {}
        else:
            return json.load(response)
    else:
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/default_plan.json', 'r') as data_file:
            plan = json.load(data_file)
    return plan
