import urllib2
import json

MAP_URL = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?Building={building}&Level={level}"
STATUS_OK = 200

def get_floor_plan(building, level):
    """
    function to download the floor plan
    :param building:
    :param level:
    :return:
    """
    url = MAP_URL.format(building=building, level=level)
    response = urllib2.urlopen(url)
    if response.getcode() != STATUS_OK:
        return {}
    else:
        return json.load(response)
