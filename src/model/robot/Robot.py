#-*- coding:UTF-8 -*-

import RPi.GPIO as GPIO
import time

from model.robot.Motors import Motors
from model.robot.TrackingModule import TrackingModule

DEFAULT_PROCESS_TIMEOUT = 10

class Robot:

    motors = None
    tracking_module = None
    process_timeout = None

    def __init__(self):
        self.init_pin_numbering_mode()

        self.motors = Motors()
        self.tracking_module = TrackingModule()
        self.process_timeout = DEFAULT_PROCESS_TIMEOUT
        
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

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        while time.time() < timeout_start + timeout:
            self.tracking_module.set_sensors_input_value()

            self.motors.run()

            if not self.tracking_module.every_sensor_over_black():
                break

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
                self.motors.sharp_right()
    
            # Handle left acute angle and left right angle 
            elif self.tracking_module.over_left_acute_angle_and_left_right_angle():
                # Turn right in place,speed is 100,delay 80ms  
                self.motors.sharp_left()
    
            # Left_sensor1 detected black line
            elif self.tracking_module.left_sensor_1_detected_black_line():
                self.motors.spin_left()
        
            # Right_sensor2 detected black line
            elif self.tracking_module.right_sensor2_detected_black_line():
                self.motors.spin_right()
    
            elif self.tracking_module.middle_right_sensor_misses_black_line():
                self.motors.left()
    
            elif self.tracking_module.middle_left_sensor_misses_black_line():
                self.motors.right()

            elif self.tracking_module.both_middle_sensors_over_black_line():
                self.motors.run()
                
            # When the every sensor is NOT over the black line, the car keeps the previous running state.
        
        self.motors.soft_stop()
        GPIO.cleanup()