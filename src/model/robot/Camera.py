#-*- coding:UTF-8 -*-

from enum import Enum
import cv2
import time
import numpy as np

from model.robot.CameraServos import CameraServos

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
YELLOW__COLOR_UPPER = np.array([34, 255, 255])
        
ORANGE_COLOR_LOWER = np.array([11, 43, 46])
ORANGE_COLOR_UPPER = np.array([25, 255, 255])

class Camera:

    color_lower = None
    color_upper = None
    camera_servos = None

    def __init__(self, color = TrackableColor.RED):
        self.camera_servos = CameraServos()
    
    #bgr8 to jpeg format
    def bgr8_to_jpeg(value, quality=75):
        return bytes(cv2.imencode('.jpg', value)[1])

    def color_track(self):
        global target_valuex, target_valuey
        t_start = time.time()
        fps = 0
        times = 0
        while True:
            ret, frame = image.read()
            frame = cv2.resize(frame, (300, 300))
            frame_ = cv2.GaussianBlur(frame,(5,5),0)                    
            hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv,color_lower,color_upper)  
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
                    xservo_pid.SystemOutput = color_x
                    xservo_pid.SetStepSignal(150)
                    xservo_pid.SetInertiaTime(0.01, 0.1)
                    target_valuex = int(1500+xservo_pid.SystemOutput)
                    yservo_pid.SystemOutput = color_y
                    yservo_pid.SetStepSignal(150)
                    yservo_pid.SetInertiaTime(0.01, 0.1)
                    target_valuey = int(1500+yservo_pid.SystemOutput)
                    time.sleep(0.008)
                    
                    if times == 5 :
                        times = 0 
                        self.camera_servos.servo_control(target_valuex,target_valuey)
