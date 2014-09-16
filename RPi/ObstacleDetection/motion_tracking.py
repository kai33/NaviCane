# http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
import cv2
import numpy as np


def show_simple_motion_tracking():
    """a simple python function to keep track of motion using
       image difference on time line

       only motion will be high lighted in white while stable objects and
       images are black
    """
    def diff_img(t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)

    cam = cv2.VideoCapture(0)

    winName = "Movement Indicator"
    cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

    # Read three images first:
    t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

    while True:
        cv2.imshow(winName, diff_img(t_minus, t, t_plus))

        # Read next image
        t_minus = t
        t = t_plus
        t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

        key = cv2.waitKey(10)
        if key == 27:  # esc
            cv2.destroyWindow(winName)
        break


def lucas_kanade_optical_flow():
    raise NotImplementedError

if __name__ == '__main__':
    show_simple_motion_tracking()
