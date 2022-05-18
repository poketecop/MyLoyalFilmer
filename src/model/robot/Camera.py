#-*- coding:UTF-8 -*-

from enum import Enum
import cv2
import time
import numpy as np

import CameraServos
from model.robot.CameraServos import CameraServos as Servos

from datetime import datetime as dt

class TrackableColor(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    ORANGE = 5
    
RED_COLOR_LOWER = np.array([0, 43, 46])
RED_COLOR_UPPER = np.array([10, 255, 255])

GREEN_COLOR_LOWER = np.array([35, 43, 46])
GREEN_COLOR_UPPER = np.array([77, 255, 255])
        
BLUE_COLOR_LOWER = np.array([100, 43, 46])
BLUE_COLOR_UPPER = np.array([124, 255, 255])

YELLOW_COLOR_LOWER = np.array([26, 43, 46])
YELLOW_COLOR_UPPER = np.array([34, 255, 255])
        
ORANGE_COLOR_LOWER = np.array([11, 43, 46])
ORANGE_COLOR_UPPER = np.array([25, 255, 255])

VIDEO_WRITER_FOURCC = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')

class Camera:

    color_lower = None
    color_upper = None
    camera_servos = None
    result = None
    image = None
    process_timeout = None

    def __init__(self, process_timeout, color = TrackableColor.RED):
        self.camera_servos = Servos()
        self.process_timeout = process_timeout
        
    def set_color_to_track(self, color_to_track):
        if color_to_track == TrackableColor.RED.name:
            self.color_lower = RED_COLOR_LOWER
            self.color_upper = RED_COLOR_UPPER
        elif color_to_track == TrackableColor.GREEN.name:
            self.color_lower = GREEN_COLOR_LOWER
            self.color_upper = GREEN_COLOR_UPPER
        elif color_to_track == TrackableColor.BLUE.name:
            self.color_lower = BLUE_COLOR_LOWER
            self.color_upper = BLUE_COLOR_UPPER
        elif color_to_track == TrackableColor.YELLOW.name:
            self.color_lower = YELLOW_COLOR_LOWER
            self.color_upper = YELLOW_COLOR_UPPER
        elif color_to_track == TrackableColor.ORANGE.name:
            self.color_lower = ORANGE_COLOR_LOWER
            self.color_upper = ORANGE_COLOR_UPPER
    
    #bgr8 to jpeg format
    def bgr8_to_jpeg(value, quality=75):
        return bytes(cv2.imencode('.jpg', value)[1])

    def init_film_capture(self):
        self.image = cv2.VideoCapture(-1)
        self.image.set(3, 640)
        self.image.set(4, 480)
        self.image.set(5, 120)   #set frame
        self.image.set(cv2.CAP_PROP_FOURCC, VIDEO_WRITER_FOURCC)
        self.image.set(cv2.CAP_PROP_BRIGHTNESS, 20) #set brihtgness -64 - 64  0.0
        self.image.set(cv2.CAP_PROP_CONTRAST, 20)   #set contrast -64 - 64  2.0

    def init_film_saving(self):
        # We need to set resolutions.
        # so, convert them from float to integer.
        frame_width = int(self.image.get(3))
        frame_height = int(self.image.get(4))
        
        size = (frame_width, frame_height)
        
        # Below VideoWriter object will create
        # a frame of above defined The output 
        # is stored in 'filename.avi' file.

        file_name = dt.now().strftime('%a_%d_%m_%Y_%H_%M_%S')

        print(file_name)

        self.result = cv2.VideoWriter('/home/pi/Videos/' + file_name + '.avi', 
                                VIDEO_WRITER_FOURCC,
                                10, size)

    def finish_filming(self):
        # When everything done, release 
        # the video capture and video 
        # write objects
        self.image.release()
        self.result.release()
            
        # Closes all the frames
        cv2.destroyAllWindows()
        
        print("The video was successfully saved")

    def film(self):
        t_start = time.time()

        self.init_film_capture()
        self.init_film_saving()
        
        while time.time() < t_start + self.process_timeout:
            ret, frame = self.image.read()
        
            if not ret:
                # Break the loop
                break
        
            # Write the frame into the
            # file 'filename.avi'
            self.result.write(frame)

        self.finish_filming()

    def color_track(self):
        self.camera_servos.init_servos_position()

        t_start = time.time()

        self.init_film_capture()
        self.init_film_saving()
        
        times = 0
        while time.time() < t_start + self.process_timeout:
            ret, frame = self.image.read()

            if not ret:
                # Break the loop
                break

            # Write the frame into the
            # file 'filename.avi'
            self.result.write(frame)

            frame = cv2.resize(frame, (300, 300))
            frame_ = cv2.GaussianBlur(frame,(5,5),0) 
            hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv,self.color_lower,self.color_upper)  
            mask = cv2.erode(mask,None,iterations=2)
            mask = cv2.dilate(mask,None,iterations=2)
            mask = cv2.GaussianBlur(mask,(3,3),0)     
            cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2] 

            if len(cnts) > 0:
                cnt = max (cnts, key = cv2.contourArea)
                (color_x,color_y),color_radius = cv2.minEnclosingCircle(cnt)
                
                if color_radius > 10:
                    times =  times +  1
                    # Mark the detected colors
                    # Proportion-Integration-Differentiation
                    self.camera_servos.xservo_pid.SystemOutput = color_x
                    self.camera_servos.xservo_pid.SetStepSignal(150)
                    self.camera_servos.xservo_pid.SetInertiaTime(0.01, 0.1)
                    target_valuex = int(CameraServos.INITIAL_X_SERVO_ANGLE + self.camera_servos.xservo_pid.SystemOutput)
                    self.camera_servos.yservo_pid.SystemOutput = color_y
                    self.camera_servos.yservo_pid.SetStepSignal(150)
                    self.camera_servos.yservo_pid.SetInertiaTime(0.01, 0.1)
                    target_valuey = int(CameraServos.INITIAL_Y_SERVO_ANGLE + self.camera_servos.yservo_pid.SystemOutput)
                    time.sleep(0.008)
                    
                    if times == 5 :
                        times = 0 
                        self.camera_servos.servo_control(target_valuex, target_valuey)

        self.finish_filming()
