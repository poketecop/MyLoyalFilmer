#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

# Definition of  button
KEY = 8

# Button detection
def key_scan(key):
    while GPIO.input(key):
        pass
    while not GPIO.input(key):
        time.sleep(0.01)
        if not GPIO.input(key):
            time.sleep(0.01)
        while not GPIO.input(key):
            pass

def percentage(percentage, value):
    return (value * percentage) / 100

def parse_arguments(argv):
    '''Parses program arguments in command format to a dictionary.
    '''
    
    result = {}
    key = None
    value = None
    for a in argv:
        if a.startswith('--'):
            key = a[2:]
        elif a.startswith('-'):
            key = a[1:]
        else:
            if not key:
                raise Exception("Argument must be preceded by a key: %s" % a)
            value = a
        if key and value:
            result[key] = value
            key = None
            value = None
    return result

def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()