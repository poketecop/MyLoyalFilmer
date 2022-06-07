from enum import Enum
import time
import RPi.GPIO as GPIO

#Definition of RGB module pin
LED_R = 22
LED_G = 27
LED_B = 24

class RGBColor(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    CYAN = 5
    WHITE = 6

class Status(Enum):
    IDDLE = 0
    LISTENING = 1

class RGBLighter:

    status = None

    def __init__(self):
        self.init_pins()
        self.status = Status.IDDLE
    
    def init_pins(self):
        # RGB pins are initialized into output mode
        GPIO.setup(LED_R, GPIO.OUT)
        GPIO.setup(LED_G, GPIO.OUT)
        GPIO.setup(LED_B, GPIO.OUT)

    def listening(self):
        print("\nListening...")
        while self.status == Status.LISTENING:
            self.light(RGBColor.BLUE)
            time.sleep(0.5)
            self.light_off()

    def error(self):
        print("\nError...")
        i = 0
        while i < 8:
            self.light(RGBColor.RED)
            time.sleep(0.5)
            self.light_off()
            i += 1

    def about_to_start(self):
        print("\nAbout to start...")
        i = 0
        while i < 3:
            self.light(RGBColor.GREEN)
            time.sleep(0.3)
            self.light(RGBColor.RED)
            time.sleep(0.3)
            self.light(RGBColor.GREEN)
            i += 1

        self.light_off()
    
    def light_off(self):
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.LOW)

    def light(self, color):
        if color == RGBColor.RED:
            GPIO.output(LED_R, GPIO.HIGH)
            GPIO.output(LED_G, GPIO.LOW)
            GPIO.output(LED_B, GPIO.LOW)
        elif color == RGBColor.GREEN:
            GPIO.output(LED_R, GPIO.LOW)
            GPIO.output(LED_G, GPIO.HIGH)
            GPIO.output(LED_B, GPIO.LOW)
        elif color == RGBColor.BLUE:
            GPIO.output(LED_R, GPIO.LOW)
            GPIO.output(LED_G, GPIO.LOW)
            GPIO.output(LED_B, GPIO.HIGH)
        elif color == RGBColor.YELLOW:
            GPIO.output(LED_R, GPIO.HIGH)
            GPIO.output(LED_G, GPIO.HIGH)
            GPIO.output(LED_B, GPIO.LOW)
        elif color == RGBColor.PURPLE:
            GPIO.output(LED_R, GPIO.HIGH)
            GPIO.output(LED_G, GPIO.LOW)
            GPIO.output(LED_B, GPIO.HIGH)
        elif color == RGBColor.CYAN:
            GPIO.output(LED_R, GPIO.LOW)
            GPIO.output(LED_G, GPIO.HIGH)
            GPIO.output(LED_B, GPIO.HIGH)
        elif color == RGBColor.WHITE:
            GPIO.output(LED_R, GPIO.HIGH)
            GPIO.output(LED_G, GPIO.HIGH)
            GPIO.output(LED_B, GPIO.HIGH)
        else:
            print("\nInvalid color")
