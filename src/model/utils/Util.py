#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

# Definition of  button
KEY = 8

class Util:

    #Button detection
    def key_scan(key):
        while GPIO.input(key):
            pass
        while not GPIO.input(key):
            time.sleep(0.01)
            if not GPIO.input(key):
                time.sleep(0.01)
            while not GPIO.input(key):
                pass