# http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
import cv2
import numpy as np


def show_simple_motion_tracking():
    """a simple python function to keep track of motion using
       image difference on time line

       only motion will be high lighted in white while stable objects and images
       are black
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
      cv2.imshow(winName, diff_img(t_minus, t, t_plus) )

      # Read next image
      t_minus = t
      t = t_plus
      t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

      key = cv2.waitKey(10)
      if key == 27: # esc
        cv2.destroyWindow(winName)
        break


def lucas_kanade_optical_flow():
    cap = cv2.VideoCapture(0)

    # params for ShiTomasi corner detection
    feature_params = dict(maxCorners = 100,
                          qualityLevel = 0.3,
                          minDistance = 7,
                          blockSize = 7 )

    # Parameters for lucas kanade optical flow
    lk_params = dict(maxLevel = 2,
                     criteria = (cv2.TERM_CRITERIA_EPS |
                                 cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Create some random colors
    color = np.random.randint(0,255,(100,3))

    # Take first frame and find corners in it
    old_frame = cap.read()[1]
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

    # Create a mask image for drawing purposes
    mask = np.zeros_like(old_frame)

    while(1):
        frame = cap.read()[1]
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray,
                                               p0, None, **lk_params)

        # Select good points
        good_new = p1[st==1]
        good_old = p0[st==1]

        # draw the tracks
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
            frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
        img = cv2.add(frame, mask)

        cv2.imshow('frame',img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

        # Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1,1,2)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    lucas_kanade_optical_flow()
