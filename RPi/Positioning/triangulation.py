import os
import sys
from time import sleep

# for running this script in shell only
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))

from Communication.WiFi import access_points_scan
from Communication.WiFi import internet_access


class WiFiRSSIPositioning(object):
    """
    Gathering of WiFi access points information and provide a rough
    estimation of current user's position
    """
    def __init__(self, building, level):
        super(WiFiRSSIPositioning, self).__init__()
        self._building = building
        self._level = level
        self._scan_results = {}
        self._get_access_points()

    def _get_access_points(self):
        access_points = []
        while not access_points:
            floor_plan = internet_access.get_floor_plan(self._building,
                                                        self._level)
            access_points = floor_plan.get('wifi', [])
        for ap in access_points:
            self._access_points[ap['macAddr']] = ap

    def get_estimated_position(self):
        self._update_scan_results()
        # triangulation part

    def _update_scan_results(self):
        for i in xrange(1, 5):
            temp_scanned_results = access_points_scan.get_scan_results()
            for sr in temp_scanned_results:
                if sr.get_mac_addr() in self._scan_results:
                    pass  # update result
                else:
                    self._scan_results[sr.get_mac_addr()] = sr
            sleep(0.1)
