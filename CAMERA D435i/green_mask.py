
import cv2 as cv
import numpy as np
#from realsense_depth import *
from fonction_tracker import tracker

# Initialize Camera Intel Realsense
#dc = DepthCamera()
stream = cv.VideoCapture(0)
ret, color_frame = stream.read()

if not stream.isOpened():
    print("Cannot open camera")
    exit()

# take first frame of the video
#ret, color_frame = dc.get_frame()

# ------------color mask-----------
# lower_green = np.array([110, 255, 255])
# upper_green = np.array([40 ,100, 100])

color_infos = (0,255,255)

# lower_red1 = np.array([180, 255, 255])
# upper_red1 = np.array([178 ,100, 50])

# lower_red2 = np.array([1, 255, 255])
# upper_red2 = np.array([0 ,100, 50])

lower_red = np.array([7, 255, 255])
upper_red = np.array([0 ,124, 118])

# --------setup window location on selected and fixed point----------



while True:

    #ret, depth_frame, color_frame = dc.get_frame()
    # color_frame_2 = color_frame
    ret, color_frame = stream.read()

    hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
    hsv = cv.medianBlur(hsv,5)
    # hsv = cv.bilateralFilter(hsv,9,75,75)

    # lower_mask = cv.inRange(hsv, upper_red1, lower_red1)
    # upper_mask = cv.inRange(hsv, upper_red2, lower_red2)
    green_mask = cv.inRange(hsv, upper_red, lower_red)

    # mask = lower_mask + upper_mask
    mask = green_mask
    mask = cv.erode(mask, None, iterations=4)
    mask = cv.dilate(mask, None, iterations=4)
    #gmask = cv.BackgroundSubtractorMOG2(history=100, varThreshold=40)

    # res = cv.bitwise_and(color_frame, color_frame, mask=mask)
    # elements = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[-2]

    # if(len(elements)>0):
    #     c = max(elements, key=cv.contourArea)
    #     ((x,y),rayon)=cv.minEnclosingCircle(c)
    #     if(rayon>20):
    #         cv.circle(res, (int(x),int(y)), int(rayon),color_infos,2)
    #         cv.circle(color_frame, (int(x),int(y)), 5 ,color_infos,10)
    #         cv.line(color_frame,(int(x),int(y)),(int(x)+150,int(y)),color_infos,2)
    #         cv.putText(color_frame, "uncul" ,(int(x)+10, int(y) -50), cv.FONT_HERSHEY_DUPLEX, 1, color_infos, 1, cv.LINE_AA)
            
    #         # Show distance for a specific point
    #         cv.circle(color_frame,(int(x),int(y)), 2, (0, 255, 255))
    #         distance = (depth_frame[int(y), int(x)])/10
    #         cv.putText(color_frame, "at {}cm".format(distance), (int(x) + 10 , int(y) - 20), cv.FONT_HERSHEY_PLAIN, 2, color_infos, 2)

    # (xr, yr, res) = tracker(color_frame,depth_frame,  mask, color_infos)
    (xr, yr, res) = tracker(color_frame,  mask, color_infos)
    # print('x : ', xr, 'y : ', yr)
    # if(xr != 0 and yr != 0):
    #     print('object is detected')
    # else:
    #     print('waiting for object')

    
    # Show distance for a specific point
    # cv.circle(color_frame,(int(xr),int(yr)), 2, (0, 255, 255))
    # distance = (depth_frame[int(yr), int(xr)])/10
    # cv.putText(color_frame, "at {}cm".format(distance), (int(xr) + 10 , int(yr) - 20), cv.FONT_HERSHEY_PLAIN, 2, color_infos, 2)            
            
    # cv.imshow('hsv', hsv)ç
    cv.imshow('mask', mask)
    cv.imshow('res', res)
    cv.imshow('color frame', color_frame)
    # cv.imshow('depth frame', depth_frame)
    # cv.imshow('color frame', color_frame)
    
    key = cv.waitKey(1)
    if key == 27:
            break;

stream.release();