import cv2 as cv
import numpy as np

from fonction_tracker import tracker
stream = cv.VideoCapture(0)
ret, color_frame = stream.read()
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
# Colors
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
fonts = cv.FONT_HERSHEY_COMPLEX
#cap = cv.VideoCapture(0)

# face detector object
#face_detector = cv.CascadeClassifier("haarcascade_frontalface_default.xml")


# focal length finder function
def focal_length(measured_distance, real_width, width_in_rf_image):
    """
    This Function Calculate the Focal Length(distance between lens to CMOS sensor), it is simple constant we can find by using
    MEASURED_DISTACE, REAL_WIDTH(Actual width of object) and WIDTH_OF_OBJECT_IN_IMAGE
    :param1 Measure_Distance(int): It is distance measured from object to the Camera while Capturing Reference image

    :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 14.3 centimeters)
    :param3 Width_In_Image(int): It is object width in the frame /image in our case in the reference image(found by Face detector)
    :retrun focal_length(Float):"""
    focal_length_value = (width_in_rf_image * measured_distance) / real_width
    return focal_length_value


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

ret, color_frame = stream.read()

hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
hsv = cv.medianBlur(hsv,5)
green_mask = cv.inRange(hsv, upper_red, lower_red)

mask = green_mask
mask = cv.erode(mask, None, iterations=4)
mask = cv.dilate(mask, None, iterations=4)

(xr, yr, res, wr, hr) = tracker(color_frame,  mask, color_infos)

print(wr)
focal_length_found = 970 # cm
print("DISTANCE FOCALE = ",focal_length_found)
while True:
    ret, color_frame = stream.read()

    hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
    hsv = cv.medianBlur(hsv,5)
    green_mask = cv.inRange(hsv, upper_red, lower_red)

    mask = green_mask
    mask = cv.erode(mask, None, iterations=4)
    mask = cv.dilate(mask, None, iterations=4)
    (xr, yr, res, wr, hr) = tracker(color_frame,  mask, color_infos)
    dist = distance_finder(focal_length_found, KNOWN_WIDTH, wr)

    print(dist)

    key = cv.waitKey(1)
    if key == 27:
        break
stream.release()
###############RED MASK
"""
while True:
    ret, color_frame = stream.read()

    hsv= cv.cvtColor(color_frame, cv.COLOR_BGR2HSV)
    hsv = cv.medianBlur(hsv,5)
    green_mask = cv.inRange(hsv, upper_red, lower_red)

    mask = green_mask
    mask = cv.erode(mask, None, iterations=4)
    mask = cv.dilate(mask, None, iterations=4)
    (xr, yr, res, wr, hr) = tracker(color_frame,  mask, color_infos)

    dist = distance_finder(focal_length_found, KNOWN_WIDTH, wr)
    print(dist)
    cv.putText(color_frame, "at {}cm".format(dist), (int(xr+wr/2) + 10 , int(yr+hr/2) - 20), cv.FONT_HERSHEY_PLAIN, 2, color_infos, 2)
    #cv.imshow('mask', mask)
    #cv.imshow('res', res)
    #cv.imshow('color frame', color_frame)
    
    
    key = cv.waitKey(1)
    if key == 27:
        break

stream.release()
"""