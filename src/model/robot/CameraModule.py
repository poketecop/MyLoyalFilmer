#-*- coding:UTF-8 -*-

from enum import Enum
import cv2
import time
import numpy as np

from model.robot import CameraServosModule
from datetime import datetime as dt

import ipywidgets.widgets as widgets
from IPython.display import display

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

SERVOS_MOVEMENT_TRACKING_DELAY = 0.008
SERVOS_MOVEMENT_TIMES_DELAY = 4
MIN_COLOR_RADIUS_TO_TRACK = 10

CENTER_X = 320
CENTER_Y = 240

class Camera:

    color_lower = None
    color_upper = None
    camera_servos = None
    result = None
    image = None
    process_timeout = None
    image_widget = None

    stop = False

    def __init__(self, process_timeout, color_to_track = TrackableColor.RED.name):
        self.camera_servos = CameraServosModule.CameraServos()
        self.process_timeout = process_timeout
        self.set_color_to_track(color_to_track)
        
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
    
    def display_frame(self, frame):
        self.image_widget.value = self.bgr8_to_jpeg(frame)

    #bgr8 to jpeg format
    def bgr8_to_jpeg(self, value, quality=75):
        return bytes(cv2.imencode('.jpg', value)[1])

    def init_film_capture(self):
        self.image = cv2.VideoCapture(-1)
        print('\Film capture initied.')
        if not self.image.isOpened():
            raise IOError("Cannot open webcam")

        self.image.set(3, 640)
        self.image.set(4, 480)
        self.image.set(5, 120)   #set frame
        self.image.set(cv2.CAP_PROP_FOURCC, VIDEO_WRITER_FOURCC)
        self.image.set(cv2.CAP_PROP_BRIGHTNESS, 20) #set brihtgness -64 - 64  0.0
        self.image.set(cv2.CAP_PROP_CONTRAST, 20)   #set contrast -64 - 64  2.0

    def get_frame_size(self):
        # We need to set resolutions.
        # so, convert them from float to integer.
        frame_width = int(self.image.get(3))
        frame_height = int(self.image.get(4))
        
        size = (frame_width, frame_height)

        return size

    def init_film_saving(self):
        # We need to set resolutions.
        size = self.get_frame_size()

        print("\nFilm saving resolution: " + str(size[0]) + " X " + str(size[1]))
        
        # Below VideoWriter object will create
        # a frame of above defined The output 
        # is stored in 'filename.avi' file.

        file_name = dt.now().strftime('%a_%d_%m_%Y_%H_%M_%S')

        print(file_name)

        self.result = cv2.VideoWriter('/home/pi/Videos/' + file_name + '.avi', 
                                VIDEO_WRITER_FOURCC,
                                10, size)

        print('\nFilm saving initied.')

    def finish_filming(self):
        self.finish_film_capture()
        self.finish_film_saving()

    def finish_film_capture(self):
        # When everything done, release 
        # the video capture
        self.image.release()
        print("The video capturing was released")
    
    def finish_film_saving(self):
        # When everything done, release 
        # the video writing
        self.result.release()
        print("The video was successfully saved")
    

    def film(self):
        t_start = time.time()

        self.init_film_capture()
        self.init_film_saving()
        
        while time.time() < t_start + self.process_timeout:
            if self.stop:
                break

            ret, frame = self.image.read()
        
            if not ret:
                # Break the loop
                break
        
            # Write the frame into the
            # file 'filename.avi'
            self.result.write(frame)

        self.finish_filming()

    def get_color_countours(self, frame):
        # frame = cv2.resize(frame, (300, 300))
        # Not used
        # frame_ = cv2.GaussianBlur(frame,(5,5),0) 
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,self.color_lower,self.color_upper)  
        mask = cv2.erode(mask,None,iterations=2)
        mask = cv2.dilate(mask,None,iterations=2)
        mask = cv2.GaussianBlur(mask,(3,3),0)     
        cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

        return cnts

    def init_film_display(self):
        (frame_width, frame_height) = self.get_frame_size()

        print("\nFilm display resolution: " + str(frame_width) + " X " + str(frame_height))

        self.image_widget = widgets.Image(format='jpeg', width=frame_width, height=frame_height)
        display(self.image_widget)

    def mark_the_detected_colors(self, frame, color_x, color_y, color_radius):
        cv2.circle(frame,(int(color_x),int(color_y)),int(color_radius),(255,0,255),2)
    
    #TODO: Mirror making it reverse.
    def calc_target_angle_x(self, current_x_angle, target_dot_x, current_x_angle_dot = CENTER_X):
        ''' Calc target value with a rule of three between current_x_angle, target_dot_x and current_x_angle_dot
        '''
        return int(current_x_angle * target_dot_x / current_x_angle_dot)

    def calc_target_angle_y(self, current_y_angle, target_dot_y, current_y_angle_dot = CENTER_Y):
        ''' Calc target value with a rule of three between current_y_angle, target_dot_y and current_y_angle_dot
        '''
        return int(current_y_angle * target_dot_y / current_y_angle_dot)

    def get_colors_position_and_color_radius(self, cnts):
        cnt = max (cnts, key = cv2.contourArea)
        (color_x,color_y), color_radius = cv2.minEnclosingCircle(cnt)

        return (color_x,color_y), color_radius

    
