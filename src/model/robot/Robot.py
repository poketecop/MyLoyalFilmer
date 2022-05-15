#-*- coding:UTF-8 -*-

import RPi.GPIO as GPIO
import time

from model.robot.Motors import Motors
from model.robot.TrackingModule import TrackingModule

class Robot:

    motors = None
    tracking_module = None

    def __init__(self):
        self.init_pin_numbering_mode()

        self.motors = Motors()
        self.tracking_module = TrackingModule()
        
    def init_pin_numbering_mode(self):
        # Set the GPIO port to BCM encoding mode.
        GPIO.setmode(GPIO.BCM)

        # Ignore warning information
        GPIO.setwarnings(False)

    def track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)

        # delay 2s	
        time.sleep(2)

        # The try/except statement is used to detect errors in the try block.
        # the except statement catches the exception information and processes it.
        
        # timeout variable can be omitted, if you use specific value in the while condition
        timeout = 10   # [seconds]

        timeout_start = time.time()

        try:
            
            while time.time() < timeout_start + timeout:
                
                self.tracking_module.set_sensors_input_value()
                
                # 4 tracking pins level status
                # 0 0 0 0
                if self.tracking_module.every_sensor_over_black():
                    break
                
                # Original conditions
               
                # Handle right acute angle and right right angle
                elif self.tracking_module.over_right_acute_angle_or_right_right_angle():
                    # Turn right in place,speed is 100,delay 80ms
                    self.motors.spin_right(35, 35)
                    time.sleep(0.08)
        
                # Handle left acute angle and left right angle 
                elif self.tracking_module.over_left_acute_angle_and_left_right_angle():
                    # Turn right in place,speed is 100,delay 80ms  
                    self.motors.spin_left(35, 35)
                    time.sleep(0.08)
        
                # Left_sensor1 detected black line
                elif self.tracking_module.left_sensor_1_detected_black_line():
                    self.motors.spin_left(35, 35)
            
                # Right_sensor2 detected black line
                elif self.tracking_module.right_sensor2_detected_black_line():
                    self.motors.spin_right(35, 35)
        
                elif self.tracking_module.middle_right_sensor_misses_black_line():
                    self.motors.left(0,40)
        
                elif self.tracking_module.middle_left_sensor_misses_black_line():
                    self.motors.right(40, 0)

                elif self.tracking_module.both_middle_sensors_over_black_line():
                    self.motors.run(50, 50)
                # When the every sensor is NOT over the black line, the car keeps the previous running state.
        
        except KeyboardInterrupt:
            pass
        
        self.motors.soft_stop()
        GPIO.cleanup()