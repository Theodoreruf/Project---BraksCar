import cv2 as cv
import numpy as np
from realsense_depth import *

#point = (400, 300)

#def show_distance(event, x, y, args, params):
#    global point


# Initialize Camera Intel Realsense
dc = DepthCamera()

# take first frame of the video
ret, depth_frame, color_frame = dc.get_frame()

#setup window location on selected and fixed point
x, y ,w, h = 640, 360, 100, 100 
point = (x, y)
track_window = (x, y, w, h)




# set up the ROI for tracking
roi = color_frame[point[1]:point[1]+h, point[0]:point[0]+w]
hsv_roi =  cv.cvtColor(roi, cv.COLOR_BGR2HSV)
mask = cv.inRange(hsv_roi, np.array([0,0,0], np.uint8), np.array([20,10,255], np.uint8))
roi_hist = cv.calcHist([hsv_roi],[0],mask,[180],[0,180])
cv.normalize(roi_hist,roi_hist,0,255,cv.NORM_MINMAX)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = (( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1))

# Create mouse event
cv.namedWindow("Color frame")
#cv2.setMouseCallback("Color frame", show_distance)

while True:
    ret, depth_frame, color_frame = dc.get_frame()
    
    if ret == True:   

        
        hsv = cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
        dst = cv.calcBackProject([hsv],[0],roi_hist,[0,180],1)
        
        # apply meanshift to get the new location
        ret, track_window = cv.CamShift(dst, track_window, term_crit)
        
        # Draw it on image
        pts = cv.boxPoints(ret)
        pts = np.int0(pts)
        img_track = cv.polylines(color_frame,[pts],True, 255,2)


        
        # Show distance for a specific point
        cv.circle(color_frame, point, 2, (0, 0, 255))
        distance = (depth_frame[point[1], point[0]])/10
        cv.putText(color_frame, "{}cm".format(distance), (point[0], point[1] - 20), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        # cv.imshow("depth frame", depth_frame)
        cv.imshow("Color frame", color_frame)
        key = cv.waitKey(1)
        if key == 27:
            break
    else:
        break
    
    