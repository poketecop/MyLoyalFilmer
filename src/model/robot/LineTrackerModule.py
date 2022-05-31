#-*- coding:UTF-8 -*-
from enum import Enum
import RPi.GPIO as GPIO
import time

CONSISTENT_CONSECUTIVE_TIMES = 1
TRACK_LOST_CONSECUTIVE_TIMES = 100000

class LineTrackingOptions(Enum):
    EVERY_SENSOR_OVER_BLACK = 0
    OVER_RIGHT_ACUTE_ANGLE_OR_RIGHT_RIGHT_ANGLE = 1
    OVER_LEFT_ACUTE_ANGLE_AND_LEFT_RIGHT_ANGLE = 2
    LEFT_SENSOR_1_DETECTED_BLACK_LINE = 3
    RIGHT_SENSOR2_DETECTED_BLACK_LINE = 4
    MIDDLE_RIGHT_SENSOR_MISSES_BLACK_LINE = 5
    MIDDLE_LEFT_SENSOR_MISSES_BLACK_LINE = 6
    BOTH_MIDDLE_SENSORS_OVER_BLACK_LINE = 7
    TRACK_LOST = 8


#TrackSensorLeftPin1 TrackSensorLeftPin2 TrackSensorRightPin1 TrackSensorRightPin2
#      3                 5                  4                   18
TrackSensorLeftPin1  =  3   #The first tracking infrared sensor pin on the left is connected to  BCM port 3 of Raspberry pi
TrackSensorLeftPin2  =  5   #The second tracking infrared sensor pin on the left is connected to  BCM port 5 of Raspberry pi
TrackSensorRightPin1 =  4    #The first tracking infrared sensor pin on the right is connected to  BCM port 4 of Raspberry pi
TrackSensorRightPin2 =  18   #The second tracking infrared sensor pin on the right is connected to  BCMport 18 of Raspberry pi

class LineTracker:

    # When the black line is detected, the corresponding indicator of the tracking module is on, and the port level is LOW.
    # When the black line is not detected, the corresponding indicator of the tracking module is off, and the port level is HIGH.
    TrackSensorLeftValue1  = None
    TrackSensorLeftValue2  = None
    TrackSensorRightValue1 = None
    TrackSensorRightValue2 = None

    current_tracking_option = None
    consecutive_tracking_option_times = None

    consistent_consecutive_times = None
    track_lost_consecutive_times = None

    def __init__(self, parameter_list, consistent_consecutive_times = CONSISTENT_CONSECUTIVE_TIMES, track_lost_consecutive_times = TRACK_LOST_CONSECUTIVE_TIMES):
        if parameter_list:
            if 'consistent_consecutive_times' in parameter_list:
                consistent_consecutive_times = parameter_list['consistent_consecutive_times']
            if 'track_lost_consecutive_times' in parameter_list:
                track_lost_consecutive_times = parameter_list['track_lost_consecutive_times']
        
        self.consecutive_tracking_option_times = 0
        self.consistent_consecutive_times = int(consistent_consecutive_times)
        self.track_lost_consecutive_times = int(track_lost_consecutive_times)
        
        GPIO.setup(TrackSensorLeftPin1,GPIO.IN)
        GPIO.setup(TrackSensorLeftPin2,GPIO.IN)
        GPIO.setup(TrackSensorRightPin1,GPIO.IN)
        GPIO.setup(TrackSensorRightPin2,GPIO.IN)

    def set_sensors_input_value(self):
        # When the black line is detected, the corresponding indicator of the tracking module is on, and the port level is LOW.
        # When the black line is not detected, the corresponding indicator of the tracking module is off, and the port level is HIGH.
        self.TrackSensorLeftValue1  = GPIO.input(TrackSensorLeftPin1)
        self.TrackSensorLeftValue2  = GPIO.input(TrackSensorLeftPin2)
        self.TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        self.TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)

    def every_sensor_over_black(self):
        # 4 tracking pins level status
        # 0 0 0 0
        if (self.TrackSensorLeftValue1 == False and 
                    self.TrackSensorLeftValue2 == False and 
                        self.TrackSensorLeftValue1 == False and
                            self.TrackSensorRightValue2 == False):

            if self.current_tracking_option == LineTrackingOptions.EVERY_SENSOR_OVER_BLACK:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to every sensor over black line.
                self.current_tracking_option = LineTrackingOptions.EVERY_SENSOR_OVER_BLACK

            return True
        
        return False

    def over_right_acute_angle_or_right_right_angle(self):
        # 4 tracking pins level status
        # 0 0 X 0
        # 1 0 X 0
        # 0 1 X 0
        
        # Handle right acute angle and right right angle
        if ((self.TrackSensorLeftValue1 == False or self.TrackSensorLeftValue2 == False) and  
                    self.TrackSensorRightValue2 == False):

            if self.current_tracking_option == LineTrackingOptions.OVER_RIGHT_ACUTE_ANGLE_OR_RIGHT_RIGHT_ANGLE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to over right acute angle or right right angle.
                self.current_tracking_option = LineTrackingOptions.OVER_RIGHT_ACUTE_ANGLE_OR_RIGHT_RIGHT_ANGLE

            return True
        
        return False

    def over_left_acute_angle_and_left_right_angle(self):
        # 4 tracking pins level status
        # 0 X 0 0       
        # 0 X 0 1 
        # 0 X 1 0 
        # Handle left acute angle and left right angle 
        if (self.TrackSensorLeftValue1 == False and 
            (self.TrackSensorRightValue1 == False or  self.TrackSensorRightValue2 == False)):

            if self.current_tracking_option == LineTrackingOptions.OVER_LEFT_ACUTE_ANGLE_AND_LEFT_RIGHT_ANGLE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to over left acute angle and left right angle.
                self.current_tracking_option = LineTrackingOptions.OVER_LEFT_ACUTE_ANGLE_AND_LEFT_RIGHT_ANGLE

            return True

        return False

    def left_sensor_1_detected_black_line(self):
        # 0 X X X
        #Left_sensor1 detected black line
        if (self.TrackSensorLeftValue1 == False):

            if self.current_tracking_option == LineTrackingOptions.LEFT_SENSOR_1_DETECTED_BLACK_LINE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to left sensor 1 detected black line.
                self.current_tracking_option = LineTrackingOptions.LEFT_SENSOR_1_DETECTED_BLACK_LINE

            return True

        return False

    def right_sensor2_detected_black_line(self):
        # X X X 0
        # Right_sensor2 detected black line
        if (self.TrackSensorRightValue2 == False):

            if self.current_tracking_option == LineTrackingOptions.RIGHT_SENSOR2_DETECTED_BLACK_LINE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to right sensor 2 detected black line.
                self.current_tracking_option = LineTrackingOptions.RIGHT_SENSOR2_DETECTED_BLACK_LINE

            return True
        
        return False

    def middle_right_sensor_misses_black_line(self):
        # 4 tracking pins level status
        # X 0 1 X
        if (self.TrackSensorLeftValue2 == False and 
            self.TrackSensorRightValue1 == True):
            if self.current_tracking_option == LineTrackingOptions.MIDDLE_RIGHT_SENSOR_MISSES_BLACK_LINE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to middle right sensor misses black line.
                self.current_tracking_option = LineTrackingOptions.MIDDLE_RIGHT_SENSOR_MISSES_BLACK_LINE

            return True
        
        return False

    def middle_left_sensor_misses_black_line(self):
        # 4 tracking pins level status
        # X 1 0 X  
        if (self.TrackSensorLeftValue2 == True and 
            self.TrackSensorRightValue1 == False):
            if self.current_tracking_option == LineTrackingOptions.MIDDLE_LEFT_SENSOR_MISSES_BLACK_LINE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to middle left sensor misses black line.
                self.current_tracking_option = LineTrackingOptions.MIDDLE_LEFT_SENSOR_MISSES_BLACK_LINE

            return True
        
        return False

    def both_middle_sensors_over_black_line(self):
        # 4 tracking pins level status
        # X 0 0 X
        if (self.TrackSensorLeftValue2 == False and 
            self.TrackSensorRightValue1 == False):
            if self.current_tracking_option == LineTrackingOptions.BOTH_MIDDLE_SENSORS_OVER_BLACK_LINE:
                self.consecutive_tracking_option_times += 1
            else:
                self.consecutive_tracking_option_times = 0
                # Set current tracking option to both middle sensors over black line.
                self.current_tracking_option = LineTrackingOptions.BOTH_MIDDLE_SENSORS_OVER_BLACK_LINE

            return True
        
        return False
    