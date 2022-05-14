#-*- coding:UTF-8 -*-

from es.uned.tfg.myloyalfilmer.model.robot.Motors import Motors
import RPi.GPIO as GPIO
import time
from es.uned.tfg.myloyalfilmer.model.robot.TrackingModule import TrackingModule

from es.uned.tfg.myloyalfilmer.model.utils.Util import Util



class Robot:

    motors = None
    tracking_module = None

    def __init__(self):
        self.motors = Motors()
        self.tracking_module = TrackingModule()
        

    def track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)

        #delay 2s	
        time.sleep(2)

        #The try/except statement is used to detect errors in the try block.
        #the except statement catches the exception information and processes it.
        
        try:
            # timeout variable can be omitted, if you use specific value in the while condition
            timeout = 10   # [seconds]

            timeout_start = time.time()

            while time.time() < timeout_start + timeout:
                
                self.tracking_module.set_sensors_input_value()
                
                #4 tracking pins level status
                # 0 0 0 0
                # Stop
                if (self.tracking_module.TrackSensorLeftValue1 == False and 
                        self.tracking_module.TrackSensorLeftValue2 == False and 
                            self.tracking_module.TrackSensorLeftValue1 == False and
                                self.tracking_module.TrackSensorRightValue2 == False):
                    break
                
                # Original conditions
                #4 tracking pins level status
                # 0 0 X 0
                # 1 0 X 0
                # 0 1 X 0
                #Turn right in place,speed is 100,delay 80ms
                #Handle right acute angle and right right angle
                elif (self.tracking_module.TrackSensorLeftValue1 == False or self.tracking_module.TrackSensorLeftValue2 == False) and  self.tracking_module.TrackSensorRightValue2 == False:
                    self.motors.spin_right(35, 35)
                    time.sleep(0.08)
        
                #4 tracking pins level status
                # 0 X 0 0       
                # 0 X 0 1 
                # 0 X 1 0       
                #Turn right in place,speed is 100,delay 80ms   
                #Handle left acute angle and left right angle 
                elif self.tracking_module.TrackSensorLeftValue1 == False and (self.tracking_module.TrackSensorRightValue1 == False or  self.tracking_module.TrackSensorRightValue2 == False):
                    self.motors.spin_left(35, 35)
                    time.sleep(0.08)
        
                # 0 X X X
                #Left_sensor1 detected black line
                elif self.tracking_module.TrackSensorLeftValue1 == False:
                    self.motors.spin_left(35, 35)
            
                # X X X 0
                #Right_sensor2 detected black line
                elif self.tracking_module.TrackSensorRightValue2 == False:
                    self.motors.spin_right(35, 35)
        
                #4 tracking pins level status
                # X 0 1 X
                elif self.tracking_module.TrackSensorLeftValue2 == False and self.tracking_module.TrackSensorRightValue1 == True:
                    self.motors.left(0,40)
        
                #4 tracking pins level status
                # X 1 0 X  
                elif self.tracking_module.TrackSensorLeftValue2 == True and self.tracking_module.TrackSensorRightValue1 == False:
                    self.motors.right(40, 0)
        
                #4 tracking pins level status
                # X 0 0 X
                elif self.tracking_module.TrackSensorLeftValue2 == False and self.tracking_module.TrackSensorRightValue1 == False:
                    self.motors.run(50, 50)
        
            # When the level of 4 pins are 1 1 1 1 , the car keeps the previous running state.
        except KeyboardInterrupt:
            pass
        
        

        GPIO.cleanup()