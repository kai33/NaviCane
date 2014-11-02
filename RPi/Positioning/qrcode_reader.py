#!/usr/bin/python
import os
import subprocess
from qrtools import QR


def decode_image(filename='default.png'):
    '''default.png is a sample image. for more qr code images, see http://qrcode.kaywa.com/'''
    my_code = QR(filename=os.path.dirname(os.path.abspath(__file__)) + '/' + filename)
    if my_code.decode():
        print my_code.data
        print my_code.data_type
        print my_code.data_to_string()
        return my_code.data
    else:
        return None


def decode_from_webcam():
    my_code = QR()
    decoded = my_code.decode_webcam()
    return decoded


def decode_from_taken_picture():
    shell_process = subprocess.Popen('raspistill -vf -hf -o cam.png', shell=True)
    shell_process.wait()
    return decode_image('cam.png')


if __name__ == '__main__':
    decode_image()
