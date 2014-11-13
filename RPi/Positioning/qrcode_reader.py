#!/usr/bin/python
import os
import picamera
from qrtools import QR


def decode_image(filename='default.png'):
    '''default.png is a sample image. for more qr code images, see http://qrcode.kaywa.com/'''
    my_code = QR(filename=os.path.dirname(os.path.abspath(__file__)) + '/' + filename)
    if my_code.decode():
        print my_code.data
        return my_code.data
    else:
        return None


def decode_from_webcam():
    my_code = QR()
    decoded = my_code.decode_webcam()
    return decoded


def decode_from_taken_picture():
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.start_preview()
        try:
            for i, filename in enumerate(camera.capture_continuous('image.jpg')):
                print i
                decode_image('image.jpg')
        finally:
            pass # camera.stop_preview()
    return None


if __name__ == '__main__':
    decode_from_taken_picture()
