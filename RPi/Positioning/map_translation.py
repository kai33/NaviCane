import os
import sys

# for running this script in shell only
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))

from Communication.WiFi import internet_access


