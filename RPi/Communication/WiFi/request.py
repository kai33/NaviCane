import requests

MAP_URL = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?Building={building}&Level={level}"

def get_floor_plan(building, level):
    """
    function to download the floor plan
    :param building:
    :param level:
    :return:
    """
    url = MAP_URL.format(building=building, level=level)
    r = requests.get(url)
    return r
