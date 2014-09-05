import requests

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
    r = requests.get(url)
    if r.status_code != STATUS_OK:
        return []
    else:
        return r.json()
