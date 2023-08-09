import cv2 as cv
import numpy as np

#from fonction_tracker import tracker

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

# distance estimation function
def distance_finder(focal_length, real_face_width, face_width_in_frame):
    """
    This Function simply Estimates the distance between object and camera using arguments(focal_length, Actual_object_width, Object_width_in_the_image)
    :param1 focal_length(float): return by the focal_length_Finder function

    :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 5.7 Inches)
    :param3 object_Width_Fra : distance Estimated
    """
    if face_width_in_frame > 0: #on évite la division par zéro 
        distance = (real_face_width * focal_length) / face_width_in_frame
    else:
        distance = 0
    return distance

def retour():
    stream = cv.VideoCapture(0)
    #ret, color_frame = stream.read()

    if not stream.isOpened():
        print("Cannot open camera")
        exit()
    color_infos = (0,255,255)
    lower_red = np.array([7, 255, 255])
    upper_red = np.array([0 ,124, 118])

    # variables
    # distance from camera to object(face) measured
    KNOWN_DISTANCE = 40  # centimeter
    # width of face in the real world or Object Plane
    KNOWN_WIDTH = 4  # centimeter

    #ret, color_frame = stream.read()

    #hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
    #hsv = cv.medianBlur(hsv,5)
    #green_mask = cv.inRange(hsv, upper_red, lower_red)

    #mask = green_mask
    #mask = cv.erode(mask, None, iterations=4)
    #mask = cv.dilate(mask, None, iterations=4)

    #(xr, yr, res, wr, hr) = tracker(color_frame,  mask, color_infos)
    #Distance focale mesuree
    focal_length_found = 970


    ###############RED MASK
    ret, color_frame = stream.read()

    hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
    hsv = cv.medianBlur(hsv,5)
    green_mask = cv.inRange(hsv, upper_red, lower_red)

    mask = green_mask
    mask = cv.erode(mask, None, iterations=4)
    mask = cv.dilate(mask, None, iterations=4)
    (xr, yr, res, wr, hr) = tracker(color_frame,  mask, color_infos)

    dist = distance_finder(focal_length_found, KNOWN_WIDTH, wr)
    cv.putText(color_frame, "at {}cm".format(dist), (int(xr+wr/2) + 10 , int(yr+hr/2) - 20), cv.FONT_HERSHEY_PLAIN, 2, color_infos, 2)
    #cv.imshow('mask', mask)
    #cv.imshow('res', res)

    #	A ENVOYER SUR LE SITE
    return color_frame
