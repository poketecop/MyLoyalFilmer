#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time
from model.robot import PID

ServoPin = 11  #S2
ServoPinB = 9  #S3

class CameraServos:

    xservo_pid = None
    yservo_pid = None

    def __init__(self):
        self.xservo_pid = PID.PositionalPID(0.8, 0.1, 0.3)
        self.yservo_pid = PID.PositionalPID(0.4, 0.1, 0.2)

    def init_servos_position(self):
        self.servo_control(1500, 1500)

    # Define a pulse function, used to simulate the pwm value
    # When base pulse is 20ms, the high level part of the pulse is controlled from 0 to 180 degrees in 0.5-2.5ms
    def servo_pulse(self, myangleA, myangleB):
        pulsewidth = myangleA
        GPIO.output(ServoPin, GPIO.HIGH)
        time.sleep(pulsewidth/1000000.0)
        GPIO.output(ServoPin, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidth/1000000.0)
        
        pulsewidthB = myangleB
        GPIO.output(ServoPinB, GPIO.HIGH)
        time.sleep(pulsewidthB/1000000.0)
        GPIO.output(ServoPinB, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidthB/1000000.0)
    
    def set_servo_to_output_mode(self):
        GPIO.setup(ServoPin, GPIO.OUT)
        GPIO.setup(ServoPinB, GPIO.OUT)

    # Control servo angle
    def servo_control(self, angle_1, angle_2):
        self.set_servo_to_output_mode()

        # Set angles inside the limits.
        if angle_1 < 500:
            angle_1 = 500
        elif angle_1 > 2500:
            angle_1 = 2500
            
        if angle_2 < 500:
            angle_2 = 500
        elif angle_2 > 2500:
            angle_2 = 2500

        self.servo_pulse(angle_1, angle_2)