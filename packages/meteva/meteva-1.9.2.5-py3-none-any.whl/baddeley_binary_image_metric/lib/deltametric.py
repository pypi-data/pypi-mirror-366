# -*-coding:utf-8-*-

import math
import sys

from meteva.method.space.baddeley_binary_image_metric.lib.distmap import *


def deltametric(a, b, p=2, c=float('inf')):
    import cv2
    if p == float('inf') or (type(p).__name__ != "str" and str(p).isnumeric() and p > 0):
        window = boundingbox(a, b)
        a = rebound(a, window)
        b = rebound(b, window)
        # dA = ndimage.morphology.distance_transform_edt(~(a['m'] == 1) + 0)
        # dB = ndimage.morphology.distance_transform_edt(~(b['m'] == 1) + 0)
        d_a = cv2.distanceTransform(np.array(~(a['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        d_b = cv2.distanceTransform(np.array(~(b['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        if not math.isinf(c):
            d_a = np.minimum(d_a, c)
            d_b = np.minimum(d_b, c)
        if math.isinf(p):
            z = np.abs(d_a - d_b)
            delta = np.max(z)
        else:
            z = np.abs(d_a - d_b) ** p
            i_z = np.mean(z)
            delta = i_z ** (1.0 / p)
        return delta
    else:
        print("p类型错误")
        raise Exception("p类型错误")
