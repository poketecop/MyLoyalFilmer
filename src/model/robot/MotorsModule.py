#-*- coding:UTF-8 -*-
from enum import Enum
import RPi.GPIO as GPIO
import time

from model.utils.RobotUtil import percentage

# Definition of  motor pins
LEFT_MOTOR_DIRECTION_FORWARD_PIN = 20
LEFT_MOTOR_DIRECTION_BACKWARD_PIN = 21
RIGHT_MOTOR_DIRECTION_FORWARD_PIN = 19
RIGHT_MOTOR_DIRECTION_BACKWARD_PIN = 26
LEFT_MOTOR_DUTY_CYCLE_PIN = 16
RIGHT_MOTOR_DUTY_CYCLE_PIN = 13

DEFAULT_DESIRED_DUTY_CYCLE = 50
SPIN_DUTY_CYCLE_PERCENTAGE = 70
OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE = 80
INWARD_MOTOR_LEAN_DUTY_CYCLE = 0

# Declare Enum named Action whose names are the names of every methods (words preceded by "def ") in the following Motors class.
class Action(Enum):
    RUN = 2
    LEFT = 6
    RIGHT = 8
    STOP = 9
    SPIN_LEFT = 11
    SPIN_RIGHT = 13
    SHARP_LEFT = 15
    SHARP_RIGHT = 17
    # Reverse
    REVERSE_RUN = 19
    REVERSE_LEFT = 21
    REVERSE_RIGHT = 23
    REVERSE_STOP = 25
    REVERSE_SPIN_LEFT = 27
    REVERSE_SPIN_RIGHT = 29
    REVERSE_SHARP_LEFT = 31
    REVERSE_SHARP_RIGHT = 33

class Motors:
    
    left_motor = None
    right_motor = None

    desired_left_duty_cycle = None
    desired_right_duty_cycle = None

    reverse_desired_left_duty_cycle = None
    reverse_desired_right_duty_cycle = None

    def __init__(self, parameter_list, desired_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE, reverse_desired_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE):
        if parameter_list:
            if 'desired_duty_cycle' in parameter_list:
                desired_duty_cycle = int(parameter_list['desired_duty_cycle'])

            if 'reverse_desired_duty_cycle' in parameter_list:
                reverse_desired_duty_cycle = int(parameter_list['reverse_desired_duty_cycle'])
        
        self.init_desired_duty_cycle(desired_duty_cycle)
        self.init_reverse_desired_duty_cycle(reverse_desired_duty_cycle)

        GPIO.setup(LEFT_MOTOR_DUTY_CYCLE_PIN,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(LEFT_MOTOR_DIRECTION_FORWARD_PIN,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(LEFT_MOTOR_DIRECTION_BACKWARD_PIN,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(RIGHT_MOTOR_DUTY_CYCLE_PIN,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(RIGHT_MOTOR_DIRECTION_FORWARD_PIN,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN,GPIO.OUT,initial=GPIO.LOW)

        # Set the PWM pin and frequency is 2000hz
        self.left_motor = GPIO.PWM(LEFT_MOTOR_DUTY_CYCLE_PIN, 2000)
        self.right_motor = GPIO.PWM(RIGHT_MOTOR_DUTY_CYCLE_PIN, 2000)
        self.left_motor.start(0)
        self.right_motor.start(0)
    
    def init_desired_duty_cycle(self, desired_duty_cycle):
        self.desired_left_duty_cycle = desired_duty_cycle
        self.desired_right_duty_cycle = desired_duty_cycle

    def init_reverse_desired_duty_cycle(self, reverse_desired_duty_cycle):
        self.reverse_desired_left_duty_cycle = reverse_desired_duty_cycle
        self.reverse_desired_right_duty_cycle = reverse_desired_duty_cycle

    #advance
    def run_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)
    
    def reverse_run_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        self.right_motor.ChangeDutyCycle(left_duty_cycle)
        self.left_motor.ChangeDutyCycle(right_duty_cycle)

    def set_lower_desired_duty_cycle(self):
        self.desired_left_duty_cycle, self.desired_right_duty_cycle = self.get_lower_duty_cycle()

    def get_lower_duty_cycle(self):
        if DEFAULT_DESIRED_DUTY_CYCLE < self.desired_left_duty_cycle:
            left_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
            right_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
        else:
            left_duty_cycle = self.desired_left_duty_cycle
            right_duty_cycle = self.desired_right_duty_cycle

        return left_duty_cycle, right_duty_cycle

    def get_reverse_lower_duty_cycle(self):
        if DEFAULT_DESIRED_DUTY_CYCLE < self.reverse_desired_left_duty_cycle:
            left_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
            right_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
        else:
            left_duty_cycle = self.reverse_desired_left_duty_cycle
            right_duty_cycle = self.reverse_desired_right_duty_cycle

        return left_duty_cycle, right_duty_cycle

    def run_with_lower_duty_cycle(self):
        left_duty_cycle, right_duty_cycle = self.get_lower_duty_cycle()

        self.run_with_duty_cycle(left_duty_cycle = left_duty_cycle, 
            right_duty_cycle = right_duty_cycle)
    
    def reverse_run_with_lower_duty_cycle(self):
        left_duty_cycle, right_duty_cycle = self.get_reverse_lower_duty_cycle()

        self.reverse_run_with_duty_cycle(left_duty_cycle = left_duty_cycle, 
            right_duty_cycle = right_duty_cycle)

    def run(self):
        self.run_with_duty_cycle(left_duty_cycle = self.desired_left_duty_cycle, 
            right_duty_cycle = self.desired_right_duty_cycle)
    
    def reverse_run(self):
        self.reverse_run_with_duty_cycle(left_duty_cycle = self.reverse_desired_left_duty_cycle, 
            right_duty_cycle = self.reverse_desired_right_duty_cycle)

    #turn left 
    def left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is stop
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        # Right motor is forward
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def reverse_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is reverse
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        # Right motor is stop
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)

        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def left(self):
        self.left_with_duty_cycle(left_duty_cycle = INWARD_MOTOR_LEAN_DUTY_CYCLE, 
            right_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )

    def reverse_left(self):
        self.reverse_left_with_duty_cycle(left_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_left_duty_cycle), 
            right_duty_cycle = INWARD_MOTOR_LEAN_DUTY_CYCLE
        )

    #turn right
    def right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is forward
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        # Right motor is stop
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def reverse_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is stop
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        # Right motor is reverse
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def right(self):
        self.right_with_duty_cycle(left_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle), 
            right_duty_cycle = INWARD_MOTOR_LEAN_DUTY_CYCLE
        )

    def reverse_right(self):
        self.reverse_right_with_duty_cycle(left_duty_cycle = INWARD_MOTOR_LEAN_DUTY_CYCLE, 
            right_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_right_duty_cycle)
        )
        
    #turn left in place
    def spin_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is reverse
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        # Right motor is forward
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def reverse_spin_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is forward
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        # Right motor is reverse
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def spin_left(self):
        self.spin_left_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )
    
    def reverse_spin_left(self):
        self.reverse_spin_left_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_right_duty_cycle)
        )
    
    def sharp_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        self.spin_left_with_duty_cycle(left_duty_cycle, right_duty_cycle), 
        time.sleep(0.08)

    def reverse_sharp_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        self.reverse_spin_left_with_duty_cycle(left_duty_cycle, right_duty_cycle), 
        time.sleep(0.08)
    
    def sharp_left(self):
        self.spin_left()
        time.sleep(0.08)

    def reverse_sharp_left(self):
        self.reverse_spin_left()
        time.sleep(0.08)

    #turn right in place
    def spin_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is forward
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        # Right motor is reverse
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)

    def reverse_spin_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        # Left motor is reverse
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.HIGH)
        # Right motor is forward
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(left_duty_cycle)
        self.right_motor.ChangeDutyCycle(right_duty_cycle)
    
    def spin_right(self):
        self.spin_right_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )

    def reverse_spin_right(self):
        self.reverse_spin_right_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.reverse_desired_right_duty_cycle)
        )

    def sharp_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        self.spin_right_with_duty_cycle(left_duty_cycle, right_duty_cycle), 
        time.sleep(0.08)

    def reverse_sharp_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        self.reverse_spin_right_with_duty_cycle(left_duty_cycle, right_duty_cycle), 
        time.sleep(0.08)
        
    def sharp_right(self):
        self.spin_right()
        time.sleep(0.08)
    
    def reverse_sharp_right(self):
        self.reverse_spin_right()
        time.sleep(0.08)

    #brake
    def brake(self):
        GPIO.output(LEFT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_FORWARD_PIN, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_DIRECTION_BACKWARD_PIN, GPIO.LOW)
    
    def final_stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def stop(self):
        self.left_motor.ChangeDutyCycle(0)
        self.right_motor.ChangeDutyCycle(0)

    def soft_final_stop(self):
        self.brake()
        time.sleep(0.08)
        self.final_stop()

    def soft_stop(self):
        self.brake()
        time.sleep(0.08)
        self.stop()