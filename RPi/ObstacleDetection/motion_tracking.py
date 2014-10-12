import numpy as np
import cv2
import cv2.cv as cv
import video
import math


def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step / 2:h:step, step / 2:w:step].reshape(2, -1)
    fx, fy = flow[y, x].T
    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


def compare_left_and_right(flow):
    middle = len(flow) / 2
    left_vector_sum = [0.0, 0.0]
    right_vector_sum = [0.0, 0.0]
    for idx, item in enumerate(flow):
        if idx < middle:
            for elem in item:
                left_vector_sum[0] = left_vector_sum[0] + elem[0]
                left_vector_sum[1] = left_vector_sum[1] + elem[1]
        else:
            for elem in item:
                right_vector_sum[0] = right_vector_sum[0] + elem[0]
                right_vector_sum[1] = right_vector_sum[1] + elem[1]
    # self strategy
    if left_vector_sum[0] > 0 and right_vector_sum[0] > 0:
        # left side object not towards, right right object towards cam
        print 'turn left'
    elif left_vector_sum[0] < 0 and right_vector_sum[0] < 0:
        # left side object towards, right right object not towards cam
        print 'turn right'
    elif math.fabs(left_vector_sum[0]) > math.fabs(right_vector_sum[0]):
        print 'turn right'
    else:
        print 'turn left'
    # for static objects only
    # left_side = left_vector_sum[0] * left_vector_sum[0] + left_vector_sum[1] * left_vector_sum[1]
    # right_side = right_vector_sum[0] * right_vector_sum[0] + right_vector_sum[1] * right_vector_sum[1]
    # if left_side > right_side:
    #     print 'turn right', left_side, right_side
    # else:
    #     print 'turn left', left_side, right_side
    # more to be done on all kinds of objects


def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:, :, 0] += np.arange(w)
    flow[:, :, 1] += np.arange(h)[:, np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res


def motion_tracking():
    cam = video.create_capture(0)
    cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640 / 2)
    cam.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480 / 2)
    ret, prev = cam.read()
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, 0.5, 3, 15, 3, 5, 1.2, 0)
        compare_left_and_right(flow)
        prevgray = gray

        cv2.imshow('flow', draw_flow(gray, flow))

        ch = 0xFF & cv2.waitKey(5)
        if ch == 27:
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    motion_tracking()
