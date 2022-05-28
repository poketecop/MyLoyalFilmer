#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

SERVO_PIN = 11  #S2
SERVO_PIN_B = 9  #S3
fPWM = 50  # Hz (not higher with software PWM)
a = 10
b = 2

DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE = 90
DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE = 90

class AlternativeCameraServos:

    initial_x_servo_angle = None
    initial_y_servo_angle = None

    current_x_servo_angle = None
    current_y_servo_angle = None

    pwm_x = None
    pwm_y = None


    def __init__(self, initial_x_servo_angle = DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, initial_y_servo_angle = DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE):
        # Current servo angles initial values are centered.
        self.current_x_servo_angle = DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE
        self.current_y_servo_angle = DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE

        self.initial_x_servo_angle = initial_x_servo_angle
        self.initial_y_servo_angle = initial_y_servo_angle

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(SERVO_PIN, GPIO.OUT)
        pwm_x = GPIO.PWM(SERVO_PIN, fPWM)
        pwm_x.start(0)

        GPIO.setup(SERVO_PIN_B, GPIO.OUT)
        pwm_x = GPIO.PWM(SERVO_PIN_B, fPWM)
        pwm_x.start(0)

    def init_servos_position(self):
        #TODO: This is not turning to times but only one time.
        self.servo_control(DEFAULT_INITIAL_CENTERED_X_SERVO_ANGLE, DEFAULT_INITIAL_CENTERED_Y_SERVO_ANGLE)
        time.sleep(2)
        self.servo_control(self.initial_x_servo_angle, self.initial_y_servo_angle)

        print('\nServos initial position set.')

    def servo_control(self, x_angle, y_angle):
        '''Control servo angle'''

        # Set angles inside the limits.
        if x_angle < 0:
            x_angle = 0
        elif x_angle > 180:
            x_angle = 180
            
        if y_angle < 0:
            y_angle = 0
        elif y_angle > 180:
            y_angle = 180

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
        self.current_x_servo_angle = myangleA

    def servo_pulse_y(self, myangleB):
        duty = self.calc_duty_cycle(myangleB)
        self.pwm_y.ChangeDutyCycle(duty)
        self.current_y_servo_angle = myangleB

    def calc_duty_cycle(self, angle):
        duty = a / 180 * angle + b
        return duty

    def test_servo_control(self):        
        self.servo_control(90)

        time.sleep(2)

        pos = 0
        while pos < 180:
            self.servo_control(pos)
            print(pos)
            pos = pos + 1
            time.sleep(0.1)

        time.sleep(2)
        pos = 180   
        while pos > 0:
            self.servo_control(pos)
            print(pos)
            pos = pos - 1
            time.sleep(0.1)
