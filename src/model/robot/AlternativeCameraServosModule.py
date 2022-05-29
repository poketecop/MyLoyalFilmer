#-*- coding:UTF-8 -*-
from enum import Enum
import RPi.GPIO as GPIO
import time

SERVO_PIN = 11  #S2
SERVO_PIN_B = 9  #S3
fPWM = 50  # Hz (not higher with software PWM)
a = 10
b = 2

DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE = 90
DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE = 90

ANGLE_SAFE_MARGIN_X = 5
ANGLE_SAFE_MARGIN_Y = 5

class DirectionX(Enum):
    NO_CHANGE = 0
    CLOCKWISE = 1
    ANTICLOCKWISE = 2

class DirectionY(Enum):
    NO_CHANGE = 0
    UP = 1
    DOWN = 2

class AlternativeCameraServos:

    initial_x_servo_angle = None
    initial_y_servo_angle = None

    current_x_servo_angle = None
    current_y_servo_angle = None

    previous_x_servo_angle = None
    previous_y_servo_angle = None

    pwm_x = None
    pwm_y = None


    def __init__(self, parameter_list, initial_x_servo_angle = DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, initial_y_servo_angle = DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE):
        if 'initial_x_servo_angle' in parameter_list:
            initial_x_servo_angle = int(parameter_list['initial_x_servo_angle'])
        
        if 'initial_y_servo_angle' in parameter_list:
            initial_y_servo_angle = int(parameter_list['initial_y_servo_angle'])
        
        # Current servo angles initial values are centered.
        self.current_x_servo_angle = DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE
        self.current_y_servo_angle = DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE

        # Initially, previous angles and current angles are the same.
        self.previous_x_servo_angle = self.current_x_servo_angle
        self.previous_y_servo_angle = self.current_y_servo_angle

        self.initial_x_servo_angle = initial_x_servo_angle
        self.initial_y_servo_angle = initial_y_servo_angle

        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.pwm_x = GPIO.PWM(SERVO_PIN, fPWM)
        self.pwm_x.start(0)

        GPIO.setup(SERVO_PIN_B, GPIO.OUT)
        self.pwm_y = GPIO.PWM(SERVO_PIN_B, fPWM)
        self.pwm_y.start(0)

    def init_servos_position(self):
        self.servo_control(DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE)
        time.sleep(2)
        self.servo_control(self.initial_x_servo_angle, self.initial_y_servo_angle)

        # Initially, previous angles and current angles are the same.
        self.previous_x_servo_angle = self.current_x_servo_angle
        self.previous_y_servo_angle = self.current_y_servo_angle

        print('\nServos initial position set.')

    def servo_control(self, x_angle, y_angle):
        '''Control servo angle'''

        # Set angles inside the limits.
        if x_angle <= 0:
            x_angle = 0 + ANGLE_SAFE_MARGIN_X
        elif x_angle >= 180:
            x_angle = 180 - ANGLE_SAFE_MARGIN_X
            
        if y_angle <= 0:
            y_angle = 0 + ANGLE_SAFE_MARGIN_Y
        elif y_angle >= 180:
            y_angle = 180 - ANGLE_SAFE_MARGIN_Y

        # If the angle is not changed, do not do anything.
        if x_angle == self.current_x_servo_angle and y_angle == self.current_y_servo_angle:
            return
        
        if x_angle == self.current_x_servo_angle:
            self.servo_pulse_y(y_angle)
            return

        # Same for y_angle.
        if y_angle == self.current_y_servo_angle:
            self.servo_pulse_x(x_angle)
            return
        
        # If not, change both angles.
        self.servo_pulse_both(x_angle, y_angle)

    def servo_pulse_both(self, myangleX, myangleY):
        self.servo_pulse_x(myangleX)
        self.servo_pulse_y(myangleY)
    
    def servo_pulse_x(self, myangleA):
        duty = self.calc_duty_cycle(myangleA)
        self.pwm_x.ChangeDutyCycle(duty)
        # Save the current angle as previous angle.
        self.previous_x_servo_angle = self.current_x_servo_angle
        self.current_x_servo_angle = myangleA

    def servo_pulse_y(self, myangleB):
        duty = self.calc_duty_cycle(myangleB)
        self.pwm_y.ChangeDutyCycle(duty)
        # Save the current angle as previous angle.
        self.previous_y_servo_angle = self.current_y_servo_angle
        self.current_y_servo_angle = myangleB

    def calc_duty_cycle(self, angle):
        duty = a / 180 * angle + b
        return duty

    def test_servo_control(self):        
        self.servo_control(DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE)

        time.sleep(2)

        pos = 0
        while pos < 100:
            self.servo_control(pos, pos)
            print(pos)
            pos = pos + 1
            time.sleep(0.1)

        time.sleep(10)

    def move_clockwise(self, degrees):
        self.servo_control(self.current_x_servo_angle - degrees, self.current_y_servo_angle)

    def move_anticlockwise(self, degrees):
        self.servo_control(self.current_x_servo_angle + degrees, self.current_y_servo_angle)

    def move_up(self, degrees):
        self.servo_control(self.current_x_servo_angle, self.current_y_servo_angle + degrees)

    def move_down(self, degrees):
        self.servo_control(self.current_x_servo_angle, self.current_y_servo_angle - degrees)

    def calc_current_direction(self):
        '''Return a list with CLOCKWISE/ANTICLOCKWISE direction and UP/DOWN direction.
        '''
        # Calculate the current direction.
        if self.current_x_servo_angle > self.previous_x_servo_angle:
            direction_x = DirectionX.CLOCKWISE
        elif self.current_x_servo_angle < self.previous_x_servo_angle:
            direction_x = DirectionX.ANTICLOCKWISE
        else:
            direction_x = DirectionX.NO_CHANGE

        if self.current_y_servo_angle > self.previous_y_servo_angle:
            direction_y = DirectionY.UP
        elif self.current_y_servo_angle < self.previous_y_servo_angle:
            direction_y = DirectionY.DOWN
        else:
            direction_y = DirectionY.NO_CHANGE

        return direction_x, direction_y

    def move_in_current_direction(self, degrees):
        '''Move in the current direction.
        '''
        direction_x, direction_y = self.calc_current_direction()
        if direction_x == DirectionX.NO_CHANGE and direction_y == DirectionY.NO_CHANGE:
            return False

        if direction_x == DirectionX.CLOCKWISE:
            self.move_clockwise(degrees)
        elif direction_x == DirectionX.ANTICLOCKWISE:
            self.move_anticlockwise(degrees)
        
        if direction_y == DirectionY.UP:
            self.move_up(degrees)
        elif direction_y == DirectionY.DOWN:
            self.move_down(degrees)

        return True
        