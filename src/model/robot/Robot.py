#-*- coding:UTF-8 -*-

import threading
import RPi.GPIO as GPIO
import time
from model.robot.Camera import Camera

from model.robot.Motors import Motors
from model.robot.TrackingModule import TrackingModule

DEFAULT_PROCESS_TIMEOUT = 10
DEFAULT_INITIAL_DELAY = 2
DEFAULT_TRACKING_LAPS = 1

class Robot:

    motors = None
    camera = None
    tracking_module = None
    process_timeout = None
    initial_delay = None
    tracking_laps = None
    threading = None

    tracking_finished = False

    def __init__(self, process_timeout = DEFAULT_PROCESS_TIMEOUT, initial_delay = DEFAULT_INITIAL_DELAY, tracking_laps = DEFAULT_TRACKING_LAPS):
        self.init_pin_numbering_mode()
        self.process_timeout = process_timeout
        self.initial_delay = initial_delay
        self.tracking_laps = tracking_laps

        self.motors = Motors()
        self.tracking_module = TrackingModule()
        self.camera = Camera(process_timeout = process_timeout)
        
        
    def init_pin_numbering_mode(self):
        # Set the GPIO port to BCM encoding mode.
        GPIO.setmode(GPIO.BCM)

        # Ignore warning information
        GPIO.setwarnings(False)

    def track_line_and_track_color(self):
        thread1 = threading.Thread(target = self.camera.color_track)
        thread1.setDaemon(True)
        thread1.start()

        thread2 = threading.Thread(target = self.track_line)
        thread2.setDaemon(True)
        thread2.start()

    def track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)

        # delay 2s	
        time.sleep(DEFAULT_INITIAL_DELAY)

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        lap = 0

        while time.time() < timeout_start + timeout:
            self.tracking_module.set_sensors_input_value()

            self.motors.run_with_lower_duty_cycle()

            if not self.tracking_module.every_sensor_over_black():
                break

        while time.time() < timeout_start + timeout:
            
            self.tracking_module.set_sensors_input_value()
            
            # 4 tracking pins level status
            # 0 0 0 0
            if self.tracking_module.every_sensor_over_black():
                lap = lap + 1

                if lap >= self.tracking_laps:
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