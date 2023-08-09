import cv2
import threading
from retour_cam import *
import numpy as np

#for ip camera use - rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' 
#for local webcam use cv2.VideoCapture(0)

class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        #self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG') 
        self.out = cv2.VideoWriter('./static/video.avi',-1,20.0, (480,320))       

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()

            if ret:
                self.out.write(frame) 

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        
        # Open a camera 
        #self.cap = cv2.VideoCapture(0)#0 to retrieve the local camera/ RTSP address to connect to a camera IP / a path to a video
        
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
        self.stream = cv2.VideoCapture(0)
    
    def __del__(self):
        self.stream.release()
    
    def get_frame(self):
        
        #ret, color_frame = stream.read()

        if not self.stream.isOpened():
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
        ret, self.color_frame = self.stream.read()

        hsv= cv2.cvtColor(self.color_frame, cv2.COLOR_BGR2HSV)
        hsv = cv2.medianBlur(hsv,5)
        green_mask = cv2.inRange(hsv, upper_red, lower_red)

        mask = green_mask
        mask = cv2.erode(mask, None, iterations=4)
        mask = cv2.dilate(mask, None, iterations=4)
        (xr, yr, res, wr, hr) = tracker(self.color_frame,  mask, color_infos)

        dist = distance_finder(focal_length_found, KNOWN_WIDTH, wr)
        cv2.putText(self.color_frame, "at {}cm".format(dist), (int(xr+wr/2) + 10 , int(yr+hr/2) - 20), cv2.FONT_HERSHEY_PLAIN, 2, color_infos, 2)

        #ret, frame = self.cap.read()

        #if ret: 
        ret, jpeg = cv2.imencode('.jpg', self.color_frame) 

        # Record video
        # if self.is_record:
        #     if self.out == None:
        #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
            
        #     ret, frame = self.cap.read()
        #     if ret:
        #         self.out.write(frame)
        # else:
        #     if self.out != None:
        #         self.out.release()
        #         self.out = None  
        
        return jpeg.tobytes()
      
        #else: 
           # return None

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.stream)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()

            
