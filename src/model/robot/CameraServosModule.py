#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time
from model.robot import PID
from model.utils.RobotUtil import sleep

SERVO_PIN = 11  #S2
SERVO_PIN_B = 9  #S3

DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE = 1500
DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE = 1500

class CameraServos:

    xservo_pid = None
    yservo_pid = None

    initial_x_servo_angle = None
    initial_y_servo_angle = None

    current_x_servo_angle = None
    current_y_servo_angle = None


    def __init__(self, initial_x_servo_angle = DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, initial_y_servo_angle = DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE):
        self.xservo_pid = PID.PositionalPID(0.8, 0.1, 0.3)
        self.yservo_pid = PID.PositionalPID(0.4, 0.1, 0.2)

        self.initial_x_servo_angle = initial_x_servo_angle
        self.initial_y_servo_angle = initial_y_servo_angle

    def init_servos_position(self):
        self.servo_control(self.initial_x_servo_angle, self.initial_y_servo_angle)

        print('\nServos initial position set.')

    # Define a pulse function, used to simulate the pwm value
    # When base pulse is 20ms, the high level part of the pulse is controlled from 0 to 180 degrees in 0.5-2.5ms
    def servo_pulse_both(self, myangleX, myangleY):
        self.servo_pulse_x(myangleX)
        self.servo_pulse_y(myangleY)
    
    def servo_pulse_x(self, myangleA):
        self.servo_pulse(SERVO_PIN, myangleA)

    def servo_pulse_y(self, myangleB):
        self.servo_pulse(SERVO_PIN_B, myangleB)

    def servo_pulse(self, pin, angle):
        pulsewidth = angle
        GPIO.output(pin, GPIO.HIGH)
        sleep(pulsewidth/1000000.0)
        GPIO.output(pin, GPIO.LOW)
        sleep(20.0/1000-pulsewidth/1000000.0)
    
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

        self.current_x_servo_angle = x_angle
        self.current_y_servo_angle = y_angle

        self.servo_pulse_both(x_angle, y_angle)
        
    def calibrate_servos(self):
        x = 1500
        y = 1500
        self.set_servo_to_output_mode()
        self.servo_pulse_both(x, y)

        x = 500
        y = 500
        self.set_servo_to_output_mode()
        self.servo_pulse_both(x, y)
        print('¿Continue going low for x? Y/N:Y')
        continue_going_low = input()

        while not continue_going_low or continue_going_low.upper() == 'Y':
            x = x - 1

            self.set_servo_to_output_mode()
            self.servo_pulse_x(x)

            print('¿Continue going low for x? Y/N:Y')
            continue_going_low = input()
        
        min_x = x

        print('¿Continue going low for y? Y/N:Y')
        continue_going_low = input()

        while not continue_going_low or continue_going_low.upper() == 'Y':
            y = y - 1

            self.set_servo_to_output_mode()
            self.servo_pulse_y(y)

            print('¿Continue going low for y? Y/N:Y')
            continue_going_low = input()

        min_y = y

        x = 1500
        y = 1500
        self.set_servo_to_output_mode()
        self.servo_pulse_both(x, y)

        x = 2500
        y = 2500
        self.set_servo_to_output_mode()
        self.servo_pulse_both(x, y)
        print('¿Continue going high for x? Y/N:Y')
        continue_going_high = input()

        while not continue_going_high or continue_going_high.upper() == 'Y':
            x = x + 1

            self.set_servo_to_output_mode()
            self.servo_pulse_x(x)

            print('¿Continue going high for x? Y/N:Y')
            continue_going_high = input()
        
        max_x = x

        print('¿Continue going high for y? Y/N:Y')
        continue_going_high = input()

        while not continue_going_high or continue_going_high.upper() == 'Y':
            y = y + 1

            self.set_servo_to_output_mode()
            self.servo_pulse_y(y)

            print('¿Continue going high for y? Y/N:Y')
            continue_going_high = input()
        
        max_y = y

        print("\nMin x:" + str(min_x))
        print("\nMin y:" + str(min_y))
        print("\nMax x:" + str(max_x))
        print("\nMax y:" + str(max_y))        
        

            