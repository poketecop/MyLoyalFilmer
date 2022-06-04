#-*- coding:UTF-8 -*-

from enum import Enum
from queue import LifoQueue, SimpleQueue
import cv2
import time
import numpy as np

from model.robot import CameraServosModule
from datetime import datetime as dt

import ipywidgets.widgets as widgets
from IPython.display import display
from model.robot import CameraServosModule

class TrackableColor(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    ORANGE = 5

# lower boundary RED color range values; Hue (0 - 10)
RED_COLOR_LOWER_1 = np.array([0, 100, 20])
RED_COLOR_UPPER_1 = np.array([10, 255, 255])
 
# upper boundary RED color range values; Hue (160 - 180)
RED_COLOR_LOWER_2 = np.array([160,100,20])
RED_COLOR_UPPER_2 = np.array([179,255,255])

GREEN_COLOR_LOWER = np.array([35, 43, 46])
GREEN_COLOR_UPPER = np.array([77, 255, 255])
        
BLUE_COLOR_LOWER = np.array([100, 43, 46])
BLUE_COLOR_UPPER = np.array([124, 255, 255])

YELLOW_COLOR_LOWER = np.array([26, 43, 46])
YELLOW_COLOR_UPPER = np.array([34, 255, 255])
        
ORANGE_COLOR_LOWER = np.array([11, 43, 46])
ORANGE_COLOR_UPPER = np.array([25, 255, 255])

VIDEO_WRITER_AVI_FOURCC = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')
VIDEO_WRITER_MP4_FOURCC = cv2.VideoWriter.fourcc(*'MP4V')

SERVOS_MOVEMENT_TRACKING_DELAY = 0.008
SERVOS_MOVEMENT_TIMES_DELAY = 1
MIN_COLOR_WIDTH_TO_TRACK = 40
MIN_COLOR_HEIGHT_TO_TRACK = 50

X_RESOLUTION = 640
Y_RESOLUTION = 480

X_Y_RESOLUTION_RELATION = X_RESOLUTION / Y_RESOLUTION

# Capturing frames and saving frames are not the same thing.
CAPTURE_FPS = 30
SAVING_FPS = 20

BRIGHTNESS = 10
CONTRAST = 30

# Center x margin just in case.
CENTER_X_MARGIN_PERCENTAGE = 0
# As the idea is to have a camera that can be used to track a color of a shirt,
# center will be the center of the shirt, so we will add a margin to place de center below.
CENTER_Y_MARGIN_PERCENTAGE = 4

ACCEPTABLE_PERCENTAGE_MARGIN_X = 14
ACCEPTABLE_PERCENTAGE_MARGIN_Y = 19

# For some reason, while motors are running, degrees become less degrees.
# Testing, 10 seemed to work better than 15 for instance.
DEGREES_TO_MOVE_TO_TRACK_COLOR = 10

DELAY_TO_STOP_AFTER_MOVING = 0.15
DELAY_TO_TRACK_AFTER_MOVING = 0.05

CONSISTENT_LOST_CONSECUTIVE_TIMES = 2

VIDEOS_PATH = '/home/pi/Videos/'

SAVING_FRAME_INTERVAL = 3

LAST_FRAME_AVAILABLE_DELAY = 0.008

class VideoFormat(Enum):
    AVI = 1
    MP4 = 2

class Camera:

    camera_servos = None
    result = None
    image = None
    image_widget = None
    processing_frame = None
    saving_frame_queue = None

    # Above module constants will be stored in these properties 
    # or the constructor parameter_list dicionary values instead.
    color_lower_1 = None
    color_upper_1 = None
    color_lower_2 = None
    color_upper_2 = None
    process_timeout = None
    servos_movement_tracking_delay = None
    servos_movement_times_delay = None
    min_color_width_to_track = None
    min_color_height_to_track = None

    center_x = None
    center_y = None

    left_acceptable_x = None
    right_acceptable_x = None
    up_acceptable_y = None
    down_acceptable_y = None

    degrees_to_move_to_track_color = None
    delay_to_stop_after_moving = None
    delay_to_track_after_moving = None
    consistent_lost_consecutive_times = None
    saving_fps = None
    video_format = None
    brightness = None
    contrast = None
    saving_frame_interval = None
    last_frame_available_delay = None

    stop = False

    def __init__(self, parameter_list, process_timeout, color_to_track = TrackableColor.RED.name, servos_movement_tracking_delay = SERVOS_MOVEMENT_TRACKING_DELAY, 
        servos_movement_times_delay = SERVOS_MOVEMENT_TIMES_DELAY, min_color_width_to_track = MIN_COLOR_WIDTH_TO_TRACK, 
        min_color_height_to_track = MIN_COLOR_HEIGHT_TO_TRACK, center_x_margin_percentage = CENTER_X_MARGIN_PERCENTAGE, center_y_margin_percentage = CENTER_Y_MARGIN_PERCENTAGE, 
        acceptable_percentage_margin_x = ACCEPTABLE_PERCENTAGE_MARGIN_X, acceptable_percentage_margin_y = ACCEPTABLE_PERCENTAGE_MARGIN_Y, degrees_to_move_to_track_color = DEGREES_TO_MOVE_TO_TRACK_COLOR, 
        delay_to_stop_after_moving = DELAY_TO_STOP_AFTER_MOVING, delay_to_track_after_moving = DELAY_TO_TRACK_AFTER_MOVING, 
        consistent_lost_consecutive_times = CONSISTENT_LOST_CONSECUTIVE_TIMES, capture_fps = CAPTURE_FPS,
        saving_fps = SAVING_FPS, video_format = VideoFormat.AVI.name, brightness = BRIGHTNESS, contrast = CONTRAST,
        saving_frame_interval = SAVING_FRAME_INTERVAL, last_frame_available_delay = LAST_FRAME_AVAILABLE_DELAY):
        ''' Uses module constants or parameter_list dictionary parameters to set self properties.
        '''
        if parameter_list:            
            if 'color_to_track' in parameter_list:
                color_to_track = parameter_list['color_to_track']
            if 'process_timeout' in parameter_list:
                process_timeout = parameter_list['process_timeout']
            if 'servos_movement_tracking_delay' in parameter_list:
                servos_movement_tracking_delay = parameter_list['servos_movement_tracking_delay']
            if 'servos_movement_times_delay' in parameter_list:
                servos_movement_times_delay = parameter_list['servos_movement_times_delay']
            if 'min_color_width_to_track' in parameter_list:
                min_color_width_to_track = parameter_list['min_color_width_to_track']
            if 'min_color_height_to_track' in parameter_list:
                min_color_height_to_track = parameter_list['min_color_height_to_track']
            if 'center_x_margin_percentage' in parameter_list:
                center_x_margin_percentage = parameter_list['center_x_margin_percentage']
            if 'center_y_margin_percentage' in parameter_list:
                center_y_margin_percentage = parameter_list['center_y_margin_percentage']
            if 'acceptable_percentage_margin_x' in parameter_list:
                acceptable_percentage_margin_x = parameter_list['acceptable_percentage_margin_x']
            if 'acceptable_percentage_margin_y' in parameter_list:
                acceptable_percentage_margin_y = parameter_list['acceptable_percentage_margin_y']
            if 'degrees_to_move_to_track_color' in parameter_list:
                degrees_to_move_to_track_color = parameter_list['degrees_to_move_to_track_color']
            if 'delay_to_stop_after_moving' in parameter_list:
                delay_to_stop_after_moving = parameter_list['delay_to_stop_after_moving']
            if 'delay_to_track_after_moving' in parameter_list:
                delay_to_track_after_moving = parameter_list['delay_to_track_after_moving']
            if 'consistent_lost_consecutive_times' in parameter_list:
                consistent_lost_consecutive_times = parameter_list['consistent_lost_consecutive_times']
            if 'capture_fps' in parameter_list:
                capture_fps = parameter_list['capture_fps']
            if 'saving_fps' in parameter_list:
                saving_fps = parameter_list['saving_fps']
            if 'video_format' in parameter_list:
                video_format = parameter_list['video_format']
            if 'brightness' in parameter_list:
                brightness = parameter_list['brightness']
            if 'contrast' in parameter_list:
                contrast = parameter_list['contrast']
            if 'saving_frame_interval' in parameter_list:
                saving_frame_interval = parameter_list['saving_frame_interval']
            if 'last_frame_available_delay' in parameter_list:
                last_frame_available_delay = parameter_list['last_frame_available_delay']

        self.set_color_to_track(color_to_track)
        self.camera_servos = CameraServosModule.CameraServos(parameter_list)

        # FIFO queue for saving frames. Every frame readed must be saved in order.
        self.saving_frame_queue = SimpleQueue()

        self.process_timeout = process_timeout
        
        self.servos_movement_tracking_delay = float(servos_movement_tracking_delay)
        self.servos_movement_times_delay = int(servos_movement_times_delay)
        self.min_color_width_to_track = int(min_color_width_to_track)
        self.min_color_height_to_track = int(min_color_height_to_track)

        self.center_x = X_RESOLUTION / 2 + ((int(center_x_margin_percentage) * X_RESOLUTION)/100)
        self.center_y = Y_RESOLUTION / 2 + ((int(center_y_margin_percentage) * Y_RESOLUTION)/100)
        
        acceptable_margin_x = (int(acceptable_percentage_margin_x) * X_RESOLUTION)/100
        acceptable_margin_y = (int(acceptable_percentage_margin_y) * Y_RESOLUTION)/100

        self.left_acceptable_x = self.center_x - acceptable_margin_x
        self.right_acceptable_x = self.center_x + acceptable_margin_x

        self.up_acceptable_y = self.center_y - acceptable_margin_y
        self.down_acceptable_y = self.center_y + acceptable_margin_y

        self.degrees_to_move_to_track_color = int(degrees_to_move_to_track_color)
        self.delay_to_stop_after_moving = float(delay_to_stop_after_moving)
        self.delay_to_track_after_moving = float(delay_to_track_after_moving)
        self.consistent_lost_consecutive_times = int(consistent_lost_consecutive_times)
        self.capture_fps = int(capture_fps)
        self.saving_fps = int(saving_fps)
        self.video_format = video_format
        self.brightness = int(brightness)
        self.contrast = int(contrast)
        self.saving_frame_interval = int(saving_frame_interval)
        self.last_frame_available_delay = int(last_frame_available_delay)
        
    def set_color_to_track(self, color_to_track):
        if color_to_track == TrackableColor.RED.name:
            self.color_lower_1 = RED_COLOR_LOWER_1
            self.color_upper_1 = RED_COLOR_UPPER_1
            self.color_lower_2 = RED_COLOR_LOWER_2
            self.color_upper_2 = RED_COLOR_UPPER_2
        elif color_to_track == TrackableColor.GREEN.name:
            self.color_lower_1 = GREEN_COLOR_LOWER
            self.color_upper_1 = GREEN_COLOR_UPPER
        elif color_to_track == TrackableColor.BLUE.name:
            self.color_lower_1 = BLUE_COLOR_LOWER
            self.color_upper_1 = BLUE_COLOR_UPPER
        elif color_to_track == TrackableColor.YELLOW.name:
            self.color_lower_1 = YELLOW_COLOR_LOWER
            self.color_upper_1 = YELLOW_COLOR_UPPER
        elif color_to_track == TrackableColor.ORANGE.name:
            self.color_lower_1 = ORANGE_COLOR_LOWER
            self.color_upper_1 = ORANGE_COLOR_UPPER
    
    def display_frame(self, frame):
        self.image_widget.value = self.bgr8_to_jpeg(frame)

    #bgr8 to jpeg format
    def bgr8_to_jpeg(self, value, quality=75):
        return bytes(cv2.imencode('.jpg', value)[1])

    def init_film_capture(self):
        self.image = cv2.VideoCapture(-1)
        # print('\Film capture initied.')
        if not self.image.isOpened():
            raise IOError("Cannot open webcam")

        self.image.set(cv2.CAP_PROP_FRAME_WIDTH , X_RESOLUTION)
        self.image.set(cv2.CAP_PROP_FRAME_HEIGHT, Y_RESOLUTION)
        self.image.set(cv2.CAP_PROP_FPS, self.capture_fps)   #set frame

        if self.video_format == VideoFormat.AVI.name:
            self.image.set(cv2.CAP_PROP_FOURCC, VIDEO_WRITER_AVI_FOURCC)
        elif self.video_format == VideoFormat.MP4.name:
            self.image.set(cv2.CAP_PROP_FOURCC, VIDEO_WRITER_MP4_FOURCC)
        
        self.image.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness) #set brihtgness -64 - 64  0.0
        self.image.set(cv2.CAP_PROP_CONTRAST, self.contrast)   #set contrast -64 - 64  2.0

    def get_frame_size(self):
        # We need to set resolutions.
        # so, convert them from float to integer.
        frame_width = int(self.image.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.image.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        size = (frame_width, frame_height)

        return size

    def init_film_saving(self):
        # We need to set resolutions.
        size = self.get_frame_size()

        # print("\nFilm saving resolution: " + str(size[0]) + " X " + str(size[1]))
        
        # Below VideoWriter object will create
        # a frame of above defined The output 
        # is stored in 'filename.avi' file.

        file_name = dt.now().strftime('%a_%d_%m_%Y_%H_%M_%S')

        print('\n' + file_name)

        if self.video_format == VideoFormat.AVI.name:
            self.result = cv2.VideoWriter(VIDEOS_PATH + file_name + '.avi', VIDEO_WRITER_AVI_FOURCC, self.saving_fps, size)
        elif self.video_format == VideoFormat.MP4.name:
            self.result = cv2.VideoWriter(VIDEOS_PATH + file_name + '.mp4', VIDEO_WRITER_MP4_FOURCC, self.saving_fps, size)

        # print('\nFilm saving initied.')

    def finish_filming(self):
        self.finish_film_capture()
        self.finish_film_saving()

    def finish_film_capture(self):
        # When everything done, release 
        # the video capture
        self.image.release()
        # print("The video capturing was released")
    
    def finish_film_saving(self):
        # When everything done, release 
        # the video writing
        self.result.release()
        # print("The video was successfully saved")
    

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
        frame_ = cv2.GaussianBlur(frame,(5,5),0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_mask = cv2.inRange(hsv, self.color_lower_1, self.color_upper_1)
        upper_mask = cv2.inRange(hsv, self.color_lower_2, self.color_upper_2)
        full_mask = lower_mask + upper_mask

        full_mask = cv2.erode(full_mask, None, iterations=2)
        full_mask = cv2.dilate(full_mask, None, iterations=2)
        full_mask = cv2.GaussianBlur(full_mask,(3,3),0)
        cnts = cv2.findContours(full_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]

        return cnts

    def get_outer_coordinates(self, cnts): 
        # Get largest contour
        c = max(cnts, key = cv2.contourArea)
        # Get bounding box
        x,y,w,h = cv2.boundingRect(c)
       
        return (x,y,w,h)

    def init_film_display(self):
        (frame_width, frame_height) = self.get_frame_size()

        # print("\nFilm display resolution: " + str(frame_width) + " X " + str(frame_height))

        self.image_widget = widgets.Image(format='jpeg', width=frame_width, height=frame_height)
        display(self.image_widget)

    def mark_the_detected_colors(self, frame, color_x,color_y, color_width, color_height):
        cv2.rectangle(frame,(color_x,color_y),(color_x+color_width,color_y+color_height),(0,255,0),2)
    
    def mirror_frame(self, frame):
        return cv2.flip(frame, 1)

    def get_colors_position_and_color_radius(self, cnts):
        cnt = max (cnts, key = cv2.contourArea)
        (color_x,color_y), color_radius = cv2.minEnclosingCircle(cnt)

        return (color_x,color_y), color_radius

    def check_and_move_servos(self, color_x, color_y, color_width, color_height, degrees):
        moved = False

        center_x = color_x + color_width / 2
        center_y = color_y + color_height / 2

        # print("\nCenter x: " + str(center_x))
        # print("\nCenter y: " + str(center_y))

        if center_x < self.left_acceptable_x:
            self.camera_servos.move_anticlockwise(degrees)
            moved = True
        elif center_x > self.right_acceptable_x:
            self.camera_servos.move_clockwise(degrees)
            moved = True

        if center_y < self.up_acceptable_y:
            self.camera_servos.move_up(degrees)
            moved = True
        elif center_y > self.down_acceptable_y:
            self.camera_servos.move_down(degrees)
            moved = True

        return moved
    
    def test_fps(self):
        self.init_film_capture()
        t_start = time.time()
        i = 0
        
        while time.time() < t_start + self.process_timeout:
            self.image.read()
            i += 1
        
        self.finish_film_capture()



    
