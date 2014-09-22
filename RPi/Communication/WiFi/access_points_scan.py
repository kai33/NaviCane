from __future__ import division
import subprocess
import re


ADDRESS_REPRESENTATION = 'Address'
ESSID_REPRESENTATION = 'ESSID'
QUALITY_REPRESENTATION = 'Quality'
FREQUENCY_REPRESENTATION = "Frequency"
SIGNAL_LEVEL_REPRESENTATION = 'Signal level'


class ScanResult(object):
    """representation of scan result of one access point"""
    def __init__(self, addr, ssid, quality, signal_level, frequency):
        self._addr = addr
        self._ssid = ssid
        self._quality = quality
        self._signal_level = signal_level
        self._frequency = frequency

    def get_mac_addr(self):
        return self._addr

    def get_ssid(self):
        return self._ssid

    def get_quality(self):
        return self._quality

    def get_signal_level(self):
        return self._signal_level

    def get_frequency(self):
        return self._frequency

    def __str__(self):
        return '{ssid}: {addr}'.format(ssid=self._ssid, addr=self._addr)

    def __repr__(self):
        return '{ssid}: {addr}'.format(ssid=self._ssid, addr=self._addr)


def get_scan_results(wifi_name='wlan0'):
    """get the result of calling iwlist [wifi] scan"""
    scan_output = subprocess.check_output(['iwlist', wifi_name, 'scan'])
    scan_list = scan_output.split('\n')
    addr = None
    quality = None
    frequency = None
    ssid = None
    signal_level = None
    results = []
    for segment in scan_list:
        if ADDRESS_REPRESENTATION in segment:
            addr = _get_address(segment.strip())
        elif QUALITY_REPRESENTATION in segment:
            quality = _get_quality(segment.strip())
            signal_level = _get_signal_level(segment.strip())
        elif FREQUENCY_REPRESENTATION in segment:
            frequency = _get_frequency(segment.strip())
        elif ESSID_REPRESENTATION in segment:
            # this should be the latest to be updated among 4
            ssid = _get_ssid(segment.strip())
            results.append(ScanResult(addr, ssid, quality, signal_level, frequency))

    return results


def _get_address(segment=''):
    addr = None
    if ADDRESS_REPRESENTATION in segment:
        try:
            m = re.search('((?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2}))', segment)
            addr = m.group(1)
        except Exception, e:
            print('regex matching address: ' + str(e))
            addr = ''
    return addr


def _get_ssid(segment=''):
    ssid = None
    if ESSID_REPRESENTATION in segment:
        try:
            m = re.search('^ESSID:\"(.+)\"$', segment)
            ssid = m.group(1)
        except Exception, e:
            print('regex matching ssid: ' + str(e))
            ssid = ''
    return ssid


def _get_quality(segment=''):
    quality = None
    if QUALITY_REPRESENTATION in segment:
        try:
            m = re.search('Quality=([0-9]+)/([0-9]+)', segment)
            actual_value = int(m.group(1))
            total_value = int(m.group(2))
            quality = actual_value / total_value
        except Exception, e:
            print('regex matching quality: ' + str(e))
            quality = 0
    return quality


def _get_signal_level(segment=''):
    signal_level = None
    if SIGNAL_LEVEL_REPRESENTATION in segment:
        try:
            m = re.search('Signal level=(-?[0-9]{2}) dBm', segment)
            signal_level = float(m.group(1))
        except Exception, e:
            print('regex matching signal_level: ' + str(e))
            signal_level = 0
    return signal_level


def _get_frequency(segment=''):
    frequency = None
    if FREQUENCY_REPRESENTATION in segment:
        try:
            # import ipdb; ipdb.set_trace()
            m = re.search('Frequency:([0-9]+\.[0-9]+) GHz', segment)
            frequency = float(m.group(1))
        except Exception, e:
            print('regex matching frequency: ' + str(e))
            frequency = 2.412
    return frequency
