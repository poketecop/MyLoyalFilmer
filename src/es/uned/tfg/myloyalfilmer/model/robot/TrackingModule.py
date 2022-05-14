#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

from es.uned.tfg.myloyalfilmer.model.utils.Util import Util

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
        GPIO.setup(KEY, GPIO.IN)
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

    