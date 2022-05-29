#-*- coding:UTF-8 -*-

from enum import Enum
import threading
import RPi.GPIO as GPIO
import time
from model.robot import CameraModule
from model.robot.Motors import Motors
from model.robot.TrackingModule import TrackingModule

DEFAULT_PROCESS_TIMEOUT = 10
DEFAULT_INITIAL_DELAY = 2
DEFAULT_TRACKING_LAPS = 1

DEGREES_TO_MOVE_TO_TRACK_COLOR = 1
DELAY_TO_TRACK_AFTER_MOVING = 0.1

class Mode(Enum):
    TRACK_LINE = 1
    FILM = 2
    COLOR_TRACK = 3
    TRACK_LINE_AND_COLOR_TRACK = 4
    CALIBRATE_CAMERA_SERVOS = 5
    TEST_COLOR_TRACK = 6
    TEST_CAMERA_SERVO_CONTROL = 7
    PRINT_PIXELS_PER_ANGLE = 8

class Robot:

    motors = None
    camera = None
    tracking_module = None
    process_timeout = None
    initial_delay = None
    tracking_laps = None
    threading = None
    mode = None

    tracking_finished = False

    def __init__(self, parameter_list, process_timeout = DEFAULT_PROCESS_TIMEOUT, initial_delay = DEFAULT_INITIAL_DELAY, tracking_laps = DEFAULT_TRACKING_LAPS, mode = Mode.TRACK_LINE_AND_COLOR_TRACK.name, debug = False):
        
        if 'mode' in parameter_list:
            mode = parameter_list['mode']
        
        if 'process_timeout' in parameter_list:
            process_timeout = int(parameter_list['process_timeout'])
        
        if 'initial_delay' in parameter_list:
            initial_delay = int(parameter_list['initial_delay'])

        if 'tracking_laps' in parameter_list:
            tracking_laps = int(parameter_list['tracking_laps'])

        if 'debug' in parameter_list:
            debug = parameter_list['debug'].lower() == 'yes'
        
        self.init_pin_numbering_mode()
        self.process_timeout = process_timeout
        self.initial_delay = initial_delay
        self.tracking_laps = tracking_laps
        self.mode = mode
        self.debug = debug

        self.motors = Motors(parameter_list)
        self.tracking_module = TrackingModule()
        self.camera = CameraModule.Camera(parameter_list, process_timeout = process_timeout)
        
    def play(self):
        try:
            if self.mode == Mode.TRACK_LINE.name:
                self.track_line()
            elif self.mode == Mode.FILM.name:
                self.camera.film()
            elif self.mode == Mode.COLOR_TRACK.name:
                self.color_track()
            elif self.mode == Mode.TRACK_LINE_AND_COLOR_TRACK.name:
                self.track_line_and_color_track()
            elif self.mode == Mode.CALIBRATE_CAMERA_SERVOS.name:
                self.camera.camera_servos.calibrate_servos()
            elif self.mode == Mode.TEST_COLOR_TRACK.name:
                self.test_color_track()
            elif self.mode == Mode.TEST_CAMERA_SERVO_CONTROL.name:
                self.camera.camera_servos.test_servo_control()
            elif self.mode == Mode.PRINT_PIXELS_PER_ANGLE.name:
                self.camera.print_pixels_per_angle()
            
        except Exception as error:
            print(error)
        finally:
            GPIO.cleanup()
    
    def init_pin_numbering_mode(self):
        # Set the GPIO port to BCM encoding mode.
        GPIO.setmode(GPIO.BCM)

        # Ignore warning information
        GPIO.setwarnings(False)

    def track_line_and_color_track(self):
        thread1 = threading.Thread(target = self.color_track)
        thread1.setDaemon(True)
        thread1.start()

        self.track_line()
        self.camera.stop = True

        while thread1.is_alive():
            time.sleep(2)

    def track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)

        # delay 2s	
        time.sleep(self.initial_delay)

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        lap = 0
        mark_lap = False

        while time.time() < timeout_start + timeout:
            self.tracking_module.set_sensors_input_value()

            self.motors.run_with_lower_duty_cycle()

            if not self.tracking_module.every_sensor_over_black():
                break

        while time.time() < timeout_start + timeout:
            
            self.tracking_module.set_sensors_input_value()
            
            # 4 tracking pins level status
            # 0 0 0 0
            if self.tracking_module.every_sensor_over_black():
                mark_lap = True
                
                if lap >= self.tracking_laps:
                    break
            elif mark_lap:
                mark_lap = False
                lap = lap + 1
            
            # Original conditions
            
            # Handle right acute angle and right right angle
            elif self.tracking_module.over_right_acute_angle_or_right_right_angle():
                # Turn right in place,speed is 100,delay 80ms
                self.motors.sharp_right()
    
            # Handle left acute angle and left right angle 
            elif self.tracking_module.over_left_acute_angle_and_left_right_angle():
                # Turn right in place,speed is 100,delay 80ms  
                self.motors.sharp_left()
    
            # Left_sensor1 detected black line
            elif self.tracking_module.left_sensor_1_detected_black_line():
                self.motors.spin_left()
        
            # Right_sensor2 detected black line
            elif self.tracking_module.right_sensor2_detected_black_line():
                self.motors.spin_right()
    
            elif self.tracking_module.middle_right_sensor_misses_black_line():
                self.motors.left()
    
            elif self.tracking_module.middle_left_sensor_misses_black_line():
                self.motors.right()

            elif self.tracking_module.both_middle_sensors_over_black_line():
                self.motors.run()
                
            # When the every sensor is NOT over the black line, the car keeps the previous running state.
        
        self.motors.soft_stop()

    def color_track(self):
        print('\n Entered color_track method.')

        self.camera.camera_servos.init_servos_position()
        # self.camera.camera_servos.init_servos_position_gradually()

        t_start = time.time()

        print('\nColor track start: ' + str(t_start))

        self.camera.init_film_capture()
        self.camera.init_film_saving()
        if self.debug:
            self.camera.init_film_display()
        
        times_to_be_consistent_trackable_color = 0
        times_interval_end_time = None
        delay_to_track_after_moving_end_time = None
        while time.time() < t_start + self.process_timeout:
            if self.camera.stop:
                break

            ret, frame = self.camera.image.read()

            if not ret:
                # Break the loop
                break

            # Write the frame into the
            # file 'filename.avi'
            if not self.debug:
                self.camera.result.write(frame)
            
            if delay_to_track_after_moving_end_time:
                if time.perf_counter() < delay_to_track_after_moving_end_time:
                    continue
                delay_to_track_after_moving_end_time = None

            cnts = self.camera.get_color_countours(frame)

            cnts_len = len(cnts)
            print('\nCountours: ' + str(cnts_len))

            if cnts_len <= 0:
                times_to_be_consistent_trackable_color = 0
                self.camera.camera_servos.move_in_current_direction(DEGREES_TO_MOVE_TO_TRACK_COLOR)
                delay_to_track_after_moving_end_time = time.perf_counter() + DELAY_TO_TRACK_AFTER_MOVING
                continue

            (color_x,color_y), color_radius = self.camera.get_colors_position_and_color_radius(cnts)
            
            print('\nColor radius:' + str(color_radius))

            if color_radius < CameraModule.MIN_COLOR_RADIUS_TO_TRACK:
                times_to_be_consistent_trackable_color = 0
                self.camera.camera_servos.move_in_current_direction(DEGREES_TO_MOVE_TO_TRACK_COLOR)
                delay_to_track_after_moving_end_time = time.perf_counter() + DELAY_TO_TRACK_AFTER_MOVING
                continue
            
            if self.debug:
                # Mark the detected colors
                self.camera.mark_the_detected_colors(frame, color_x, color_y, color_radius)
                self.camera.result.write(frame)
                self.camera.display_frame(frame)
                
            # Consistent trackable color.
            if times_to_be_consistent_trackable_color < CameraModule.SERVOS_MOVEMENT_TIMES_DELAY:
                # Can't use sleep if not necessary to keep capturing video
                # So we will check intervals of SERVOS_MOVEMENT_TRACKING_DELAY until SERVOS_MOVEMENT_TIMES_DELAY times.
                if not times_interval_end_time:
                    times_interval_end_time = time.perf_counter() + CameraModule.SERVOS_MOVEMENT_TRACKING_DELAY
                    # Calc for an interval.
                    continue
                
                # Check for an interval.
                if time.perf_counter() < times_interval_end_time:
                    continue

                # One less time to be a consistent trackable color.
                times_to_be_consistent_trackable_color =  times_to_be_consistent_trackable_color +  1
                # Reset the interval.
                times_interval_end_time = None
                continue

            # Reset the times.
            times_to_be_consistent_trackable_color = 0
            times_interval_end_time = None
            
            self.camera.check_and_move_servos(color_x, color_y, color_radius, DEGREES_TO_MOVE_TO_TRACK_COLOR)
            delay_to_track_after_moving_end_time = time.perf_counter() + DELAY_TO_TRACK_AFTER_MOVING

        self.camera.finish_filming()
        
        return 0

    def test_color_track(self):
        print('\n Entered color_track method.')

        self.camera.init_film_capture()
        self.camera.init_film_display()
        self.camera.init_film_saving()
        
        i = 0

        while i < 3:
            ret, frame = self.camera.image.read()

            if not ret:
                # Break the loop
                break

            # Write the frame into the
            # file 'filename.avi'
            self.camera.result.write(frame)

            cnts = self.camera.get_color_countours(frame)

            cnts_len = len(cnts)
            print('\nCountours: ' + str(cnts_len))

            if cnts_len > 0:
                (color_x,color_y), color_radius = self.camera.get_colors_position_and_color_radius(cnts)                
                print('\nColor radius:' + str(color_radius))

                if color_radius > CameraModule.MIN_COLOR_RADIUS_TO_TRACK:
                    # Mark the detected colors
                    self.camera.mark_the_detected_colors(frame, color_x, color_y, color_radius)
            
            self.camera.display_frame(frame)

            i = self.chech_test_position(color_x, color_y, i)
           
        self.camera.finish_filming()

    def chech_test_position(self, color_x, color_y, i):
        print('\n¿Are you in the desired' + str(i) + ' test position? Y/N:N')

        in_position = input()

        if not in_position or in_position.upper == 'N':
            print('\nMove to the desired' + str(i) + ' test position.')
            return i
        
        print('\nWrite down X and Y value: X = ' + str(color_x) + ' Y = ' + str(color_y))

        return i + 1

        



                    
                    
