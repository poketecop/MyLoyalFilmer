#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time
from model.robot import PID

SERVO_PIN = 11  #S2
SERVO_PIN_B = 9  #S3

INITIAL_X_SERVO_ANGLE = 1500
INITIAL_Y_SERVO_ANGLE = 1500

class CameraServos:

    xservo_pid = None
    yservo_pid = None

    def __init__(self):
        self.xservo_pid = PID.PositionalPID(0.8, 0.1, 0.3)
        self.yservo_pid = PID.PositionalPID(0.4, 0.1, 0.2)

    def init_servos_position(self):
        self.servo_control(INITIAL_X_SERVO_ANGLE, INITIAL_Y_SERVO_ANGLE)

    # Define a pulse function, used to simulate the pwm value
    # When base pulse is 20ms, the high level part of the pulse is controlled from 0 to 180 degrees in 0.5-2.5ms
    def servo_pulse(self, myangleA, myangleB):
        pulsewidth = myangleA
        GPIO.output(SERVO_PIN, GPIO.HIGH)
        time.sleep(pulsewidth/1000000.0)
        GPIO.output(SERVO_PIN, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidth/1000000.0)
        
        pulsewidthB = myangleB
        GPIO.output(SERVO_PIN_B, GPIO.HIGH)
        time.sleep(pulsewidthB/1000000.0)
        GPIO.output(SERVO_PIN_B, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidthB/1000000.0)
    
    def set_servo_to_output_mode(self):
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        GPIO.setup(SERVO_PIN_B, GPIO.OUT)

    # Control servo angle
    def servo_control(self, x_angle, y_angle):
        self.set_servo_to_output_mode()

        # Set angles inside the limits.
        if x_angle < 500:
            x_angle = 500
        elif x_angle > 2500:
            x_angle = 2500
            
        if y_angle < 500:
            y_angle = 500
        elif y_angle > 2500:
            y_angle = 2500

        self.servo_pulse(x_angle, y_angle)