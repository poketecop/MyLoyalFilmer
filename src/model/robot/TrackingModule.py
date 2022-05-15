#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time


#TrackSensorLeftPin1 TrackSensorLeftPin2 TrackSensorRightPin1 TrackSensorRightPin2
#      3                 5                  4                   18
TrackSensorLeftPin1  =  3   #The first tracking infrared sensor pin on the left is connected to  BCM port 3 of Raspberry pi
TrackSensorLeftPin2  =  5   #The second tracking infrared sensor pin on the left is connected to  BCM port 5 of Raspberry pi
TrackSensorRightPin1 =  4    #The first tracking infrared sensor pin on the right is connected to  BCM port 4 of Raspberry pi
TrackSensorRightPin2 =  18   #The second tracking infrared sensor pin on the right is connected to  BCMport 18 of Raspberry pi

class TrackingModule:

    # When the black line is detected, the corresponding indicator of the tracking module is on, and the port level is LOW.
    # When the black line is not detected, the corresponding indicator of the tracking module is off, and the port level is HIGH.
    TrackSensorLeftValue1  = None
    TrackSensorLeftValue2  = None
    TrackSensorRightValue1 = None
    TrackSensorRightValue2 = None

    def __init__(self):
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
        return (self.TrackSensorLeftValue1 == False and 
                    self.TrackSensorLeftValue2 == False and 
                        self.TrackSensorLeftValue1 == False and
                            self.TrackSensorRightValue2 == False)
    
    def consistent_every_sensor_over_black(self):
        if self.every_sensor_over_black():
            # Only one time is considered as error
            time.sleep(0.08)
            self.set_sensors_input_value()

            return self.every_sensor_over_black()

        return False

    def over_right_acute_angle_or_right_right_angle(self):
        # 4 tracking pins level status
        # 0 0 X 0
        # 1 0 X 0
        # 0 1 X 0
        
        # Handle right acute angle and right right angle
        return ((self.TrackSensorLeftValue1 == False or self.TrackSensorLeftValue2 == False) and  
                    self.TrackSensorRightValue2 == False)

    def over_left_acute_angle_and_left_right_angle(self):
        # 4 tracking pins level status
        # 0 X 0 0       
        # 0 X 0 1 
        # 0 X 1 0 
        # Handle left acute angle and left right angle 
        return (self.TrackSensorLeftValue1 == False and 
            (self.TrackSensorRightValue1 == False or  self.TrackSensorRightValue2 == False))

    def left_sensor_1_detected_black_line(self):
        # 0 X X X
        #Left_sensor1 detected black line
        return (self.TrackSensorLeftValue1 == False)

    def right_sensor2_detected_black_line(self):
        # X X X 0
        # Right_sensor2 detected black line
        return (self.TrackSensorRightValue2 == False)

    def middle_right_sensor_misses_black_line(self):
        # 4 tracking pins level status
        # X 0 1 X
        return (self.TrackSensorLeftValue2 == False and 
            self.TrackSensorRightValue1 == True)

    def middle_left_sensor_misses_black_line(self):
        # 4 tracking pins level status
        # X 1 0 X  
        return (self.TrackSensorLeftValue2 == True and 
            self.TrackSensorRightValue1 == False)

    def both_middle_sensors_over_black_line(self):
        # 4 tracking pins level status
        # X 0 0 X
        return (self.TrackSensorLeftValue2 == False and 
            self.TrackSensorRightValue1 == False)
    