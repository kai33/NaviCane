import os
import sys
import math
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
            self._access_points[ap['macAddr'][:14]] = ap

    def get_estimated_position(self, wifi_name):
        """
        a rough estimated position based on trilateration
        """
        # needs testsing
        self._update_scan_results(wifi_name)
        if (len(self._scan_results) <= 3):
            self._update_scan_results(wifi_name)
        if (len(self._scan_results) <= 3):
            print 'cannot get enough scan results'
            return None
        dis_table = {}
        print self._scan_results
        for sr in self._scan_results.values():
            node = self._access_points[sr.get_mac_addr()[:14]]
            temp_dis = self._get_distance(sr.get_signal_level(), sr.get_frequency())
            dis_table[sr.get_mac_addr()] = {'x': node['x'], 'y': node['y'], 'd': temp_dis}
        sorted_keys = sorted(dis_table, key=lambda x: dis_table[x]['d'])
        return self._get_trilateration_point(float(dis_table[sorted_keys[0]]['x']),
                                             float(dis_table[sorted_keys[0]]['y']),
                                             float(dis_table[sorted_keys[0]]['d']),
                                             float(dis_table[sorted_keys[1]]['x']),
                                             float(dis_table[sorted_keys[1]]['y']),
                                             float(dis_table[sorted_keys[1]]['d']),
                                             float(dis_table[sorted_keys[2]]['x']),
                                             float(dis_table[sorted_keys[2]]['y']),
                                             float(dis_table[sorted_keys[2]]['d']))

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

        ref: http://rvmiller.com/2013/05/part-1-wifi-based-trilateration-on-android/
             http://stackoverflow.com/questions/11217674/how-to-calculate-distance-
             from-wifi-router-using-signal-strength

        mark : http://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Mobility/WiFiLBS-DG/wifich5.html
               # Figure 5-10 An Example of the Relationship Between RSSI and Distance

        verification : http://www.radiolabs.com/stations/wifi_calc.html

        signal_level: (dB)
        frequency: (MHz)
        return: distance in cm
        """
        exp = (27.55 - 20 * math.log10(frequency) + math.fabs(signal_level)) / 20.0
        return (10 ** exp) * 100

    def _update_scan_results(self, wifi_name):
        # import ipdb; ipdb.set_trace()
        for i in xrange(1, 7):
            temp_scanned_results = access_points_scan.get_scan_results(wifi_name)
            for sr in temp_scanned_results:
                if sr.get_mac_addr()[:14] in self._access_points and sr.get_ssid() == 'NUS':
                    if sr.get_mac_addr()[:14] in self._scan_results:
                        print sr.get_mac_addr()
                        self._scan_results[sr.get_mac_addr()[:14]].average(sr)
                    else:
                        self._scan_results[sr.get_mac_addr()] = sr
            sleep(0.5)

if __name__ == '__main__':
    positioning = WiFiPositioning('COM1', '2')
    p = positioning.get_estimated_position('eth1')
    print p
