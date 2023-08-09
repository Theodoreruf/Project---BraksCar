import cv2 as cv
import numpy as np
#import pyrealsense2 


def tracker(color_frame, mask, color_infos):

    res = cv.bitwise_and(color_frame,color_frame, mask=mask)
    elements = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[-2]
    x, y= 0, 0
    w, h = 0,0
    if(len(elements)>0):
        c = max(elements, key=cv.contourArea)
        # ((x,y),rayon)=cv.minEnclosingCircle(c)
        x,y,w,h = cv.boundingRect(c)
        if(w*h>10):
            cv.rectangle(res, (x,y),(x+w,y+h),color_infos,2) #contour objet
            cv.circle(color_frame, (int(x+w/2),int(y+h/2)), 5 ,color_infos,10) #point centrzl de l'objet
            cv.line(color_frame,(int(x+w/2),int(y+h/2)),(int(x+w/2)+150,int(y+h/2)),color_infos,2)
            cv.putText(color_frame, "object" ,(int(x+w/2)+10, int(y+h/2) -50), cv.FONT_HERSHEY_DUPLEX, 1, color_infos, 1, cv.LINE_AA)
            
            #print('object is detected')
        # Show distance for a specific point
        # cv.circle(color_frame,(int(x),int(y)), 2, (0, 255, 255))
        # distance = (depth_frame[int(y), int(x)])/10
        # cv.putText(color_frame, "at {}cm".format(distance), (int(x) + 10 , int(y) - 20), cv.FONT_HERSHEY_PLAIN, 2, color_infos, 2)            
    return (x, y, res, w, h)