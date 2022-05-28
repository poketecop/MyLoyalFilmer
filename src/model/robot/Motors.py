#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

from model.utils.RobotUtil import percentage

# Definition of  motor pins
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13

DEFAULT_DESIRED_DUTY_CYCLE = 50
SPIN_DUTY_CYCLE_PERCENTAGE = 70
OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE = 80
INWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE = 10

class Motors:
    
    pwm_ENA = None
    pwm_ENB = None

    desired_left_duty_cycle = None
    desired_right_duty_cycle = None

    def __init__(self, parameter_list, desired_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE):
        if 'desired_duty_cycle' in parameter_list:
            desired_duty_cycle = int(parameter_list['desired_duty_cycle'])
        
        self.init_desired_duty_cycle(desired_duty_cycle)

        GPIO.setup(ENA,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(ENB,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)

        # Set the PWM pin and frequency is 2000hz
        self.pwm_ENA = GPIO.PWM(ENA, 2000)
        self.pwm_ENB = GPIO.PWM(ENB, 2000)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)
    
    def init_desired_duty_cycle(self, desired_duty_cycle):
        self.desired_left_duty_cycle = desired_duty_cycle
        self.desired_right_duty_cycle = desired_duty_cycle

    #advance
    def run_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)

    def run_with_lower_duty_cycle(self):
        if DEFAULT_DESIRED_DUTY_CYCLE < self.desired_left_duty_cycle:
            left_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
            right_duty_cycle = DEFAULT_DESIRED_DUTY_CYCLE
        else:
            left_duty_cycle = self.desired_left_duty_cycle
            right_duty_cycle = self.desired_right_duty_cycle

        self.run_with_duty_cycle(left_duty_cycle = left_duty_cycle, 
            right_duty_cycle = right_duty_cycle)

    def run(self):
        self.run_with_duty_cycle(left_duty_cycle = self.desired_left_duty_cycle, 
            right_duty_cycle = self.desired_right_duty_cycle)

    #back
    def back_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)
    
    def back(self):
        self.back_with_duty_cycle(left_duty_cycle = self.desired_left_duty_cycle, 
            right_duty_cycle = self.desired_right_duty_cycle)
        
    #turn left 
    def left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)

    def left(self):
        self.left_with_duty_cycle(left_duty_cycle = percentage(INWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )

    #turn right
    def right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)

    def right(self):
        self.right_with_duty_cycle(left_duty_cycle = percentage(OUTWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(INWARD_MOTOR_LEAN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )
        
    #turn left in place
    def spin_left_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)

    def spin_left(self):
        self.spin_left_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )
    
    def sharp_left(self):
        self.spin_left()
        time.sleep(0.08)

    #turn right in place
    def spin_right_with_duty_cycle(self, left_duty_cycle, right_duty_cycle):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(left_duty_cycle)
        self.pwm_ENB.ChangeDutyCycle(right_duty_cycle)
    
    def spin_right(self):
        self.spin_right_with_duty_cycle(left_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_left_duty_cycle), 
            right_duty_cycle = percentage(SPIN_DUTY_CYCLE_PERCENTAGE, self.desired_right_duty_cycle)
        )

    def sharp_right(self):
        self.spin_right()
        time.sleep(0.08)

    #brake
    def brake(self):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
    
    def stop(self):
        self.pwm_ENA.stop()
        self.pwm_ENB.stop()

    def soft_stop(self):
        self.brake()
        time.sleep(0.08)
        self.stop()