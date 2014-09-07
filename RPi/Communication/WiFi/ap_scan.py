import subprocess
import re

ADDRESS_REPRESENTATION = 'Address'
ESSID_REPRESENTATION = 'ESSID'
QUALITY_REPRESENTATION = 'Quality'
SIGNAL_LEVEL_REPRESENTATION = 'Signal level'


def get_address(segment=''):
    addr = None
    if ADDRESS_REPRESENTATION in segment:
        try:
            m = re.search('((?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2}))', segment)
            addr = m.group(1)
        except Exception, e:
            addr = ''
    return addr


def get_ssid(segment=''):
    ssid = None
    if ESSID_REPRESENTATION in segment:
        try:
            m = re.search('^ESSID:\"(.+)\"$', segment)
            ssid = m.group(1)
        except Exception, e:
            ssid = ''
    return ssid


def get_quality(segment=''):
    quality = None
    if QUALITY_REPRESENTATION in segment:
        try:
            m = re.search('Quality=([0-9]{2}/[0-9]{2})', segment)
            quality = m.group(1)
        except Exception, e:
            quality = ''
    return quality


def get_signal_level(segment=''):
    signal_level = None
    if SIGNAL_LEVEL_REPRESENTATION in segment:
        try:
            m = re.search('Signal level=(-[0-9]{2}) dBm', segment)
            signal_level = m.group(1)
        except Exception, e:
            signal_level = ''
    return signal_level


def get_ap_scan_result(wifi_name='wlan0'):
    """get the result of calling iwlist [wifi] scan"""
    scan_output = subprocess.check_output(['iwlist', wifi_name, 'scan'])
    scan_list = scan_output.split('\n')
    filtered_segments = []
    for segment in scan_list:
        if ADDRESS_REPRESENTATION in segment:
            filtered_segments.append(get_address(segment.strip()))
        elif ESSID_REPRESENTATION in segment:
            filtered_segments.append(get_ssid(segment.strip()))
        elif QUALITY_REPRESENTATION in segment:
            filtered_segments.append(get_quality(segment.strip()))
            filtered_segments.append(get_signal_level(segment.strip()))

    return filtered_segments
