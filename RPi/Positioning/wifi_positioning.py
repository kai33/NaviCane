import os
import sys
import math
import operator
from time import sleep

# for running this script in shell only
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             os.pardir))

from Communication.WiFi import access_points_scan
from Communication.WiFi import internet_access


class WiFiPositioning(object):
    """
    Gathering of WiFi access points information and provide a rough
    estimation of current user's position
    """
    def __init__(self, building, level):
        super(WiFiPositioning, self).__init__()
        self._building = building
        self._level = level
        self._scan_results = {}
        self._access_points = {}  # macAddr: info
        self._get_access_points()

    def _get_access_points(self):
        """
        download access points information from server. cache that afterwards
        """
        access_points = []
        while not access_points:
            floor_plan = internet_access.get_floor_plan(self._building,
                                                        self._level)
            access_points = floor_plan.get('wifi', [])
        for ap in access_points:
            self._access_points[ap['macAddr']] = ap

    def get_estimated_position(self, wifi_name):
        """
        a rough estimated position based on trilateration
        """
        # needs testsing
        self._update_scan_results(wifi_name)
        if (len(self._scan_results) <= 3):
            return None
        dis_table = {}
        for sr in self._scan_results:
            node = self._access_points[sr.get_mac_addr()]
            temp_dis = self._get_distance(sr.get_signal_level(), sr.get_frequency())
            dis_table[sr.get_mac_addr()] = {'x': node['x'], 'y': node['y'], 'd': temp_dis}
        sorted_dis_list = sorted(dis_table, key=operator.itemgetter(1)['d']).values()
        return self._get_trilateration_point(sorted_dis_list[0]['x'],
                                             sorted_dis_list[0]['y'],
                                             sorted_dis_list[0]['d'],
                                             sorted_dis_list[1]['x'],
                                             sorted_dis_list[1]['y'],
                                             sorted_dis_list[1]['d'],
                                             sorted_dis_list[2]['x'],
                                             sorted_dis_list[2]['y'],
                                             sorted_dis_list[2]['d'])

    def _get_trilateration_point(self, x1, y1, d1, x2, y2, d2, x3, y3, d3):
        """
        ref: http://www.ijisme.org/attachments/File/v1i10/J04470911013.pdf

        _get_trilateration_point(0, 0, 3, 4*1.732, 0, 3, 2*1.732, 4.732, 3)
        {'y': 1.098111580726966, 'x': 3.464}
        """
        # this method is also roughly fine
        va = ((d2 * d2 - d3 * d3) - (x2 * x2 - x3 * x3) - (y2 * y2 - y3 * y3)) / 2
        vb = ((d2 * d2 - d1 * d1) - (x2 * x2 - x1 * x1) - (y2 * y2 - y1 * y1)) / 2
        y_point = (vb * (x3 - x2) - va * (x1 - x2)) / ((y1 - y2) * (x3 - x2) - (y3 - y2) * (x1 - x2))
        x_point = (va - y_point * (y3 - y2)) / (x3 - x2)
        return {'x': x_point, 'y': y_point}

    def _get_distance(self, signal_level, frequency):
        """
        Making use of free space path loss theory. Not working well with
        obstacles blocking the signal. needs improvement

        signal_level: (dB)
        frequency: (MHz)
        """
        exp = (27.55 - 20 * math.log10(frequency) + math.fabs(signal_level)) / 20.0
        return 10 ** exp * 100

    def _update_scan_results(self, wifi_name):
        import ipdb; ipdb.set_trace()
        # this method should be roughly fine
        for i in xrange(1, 5):
            temp_scanned_results = access_points_scan.get_scan_results(wifi_name)
            for sr in temp_scanned_results:
                if sr.get_mac_addr() in self._access_points:
                    if sr.get_mac_addr() in self._scan_results:
                        self._scan_results[sr.get_mac_addr()].average(sr)
                    else:
                        self._scan_results[sr.get_mac_addr()] = sr
            sleep(0.01)
