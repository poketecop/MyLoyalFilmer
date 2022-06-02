#-*- coding:UTF-8 -*-

from enum import Enum
import threading
import RPi.GPIO as GPIO
import time
from model.robot import CameraModule
from model.robot.Motors import Motors
from model.robot import LineTrackerModule
import traceback

DEFAULT_PROCESS_TIMEOUT = 10
DEFAULT_INITIAL_DELAY = 2
DEFAULT_TRACKING_LAPS = 1

class Mode(Enum):
    TRACK_LINE = 1
    FILM = 2
    COLOR_TRACK = 3
    TRACK_LINE_AND_COLOR_TRACK = 4
    CALIBRATE_CAMERA_SERVOS = 5
    TEST_CAMERA_SERVO_CONTROL = 7
    # print_PIXELS_PER_ANGLE = 8
    TRACK_LINE_AND_TEST_CAMERA_SERVO_CONTROL = 9

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
        if parameter_list:
            if 'mode' in parameter_list:
                mode = parameter_list['mode']
            
            if 'process_timeout' in parameter_list:
                process_timeout = parameter_list['process_timeout']
            
            if 'initial_delay' in parameter_list:
                initial_delay = parameter_list['initial_delay']

            if 'tracking_laps' in parameter_list:
                tracking_laps = parameter_list['tracking_laps']

            if 'debug' in parameter_list:
                debug = parameter_list['debug'].lower() == 'yes'
        
        self.init_pin_numbering_mode()
        self.process_timeout = int(process_timeout)
        self.initial_delay = int(initial_delay)
        self.tracking_laps = int(tracking_laps)
        self.mode = mode
        self.debug = debug

        self.motors = Motors(parameter_list)
        self.tracking_module = LineTrackerModule.LineTracker(parameter_list)
        self.camera = CameraModule.Camera(parameter_list, process_timeout = process_timeout)
        
    def play(self):
        try:
            if self.mode == Mode.TRACK_LINE.name:
                self.track_line()
            elif self.mode == Mode.FILM.name:
                self.camera.film()
            elif self.mode == Mode.COLOR_TRACK.name:
                self.save_film_and_color_track()
            elif self.mode == Mode.TRACK_LINE_AND_COLOR_TRACK.name:
                self.track_line_and_color_track()
            elif self.mode == Mode.CALIBRATE_CAMERA_SERVOS.name:
                self.camera.camera_servos.calibrate_servos()
            elif self.mode == Mode.TEST_CAMERA_SERVO_CONTROL.name:
                self.camera.camera_servos.test_servo_control()
            elif self.mode == Mode.TRACK_LINE_AND_TEST_CAMERA_SERVO_CONTROL.name:
                self.track_line_and_test_camera_servo_control()
            
        except Exception as error:
            print(error)
            print('\n\n' + traceback.format_exc())
        finally:
            GPIO.cleanup()
    
    def init_pin_numbering_mode(self):
        # Set the GPIO port to BCM encoding mode.
        GPIO.setmode(GPIO.BCM)

        # Ignore warning information
        GPIO.setwarnings(False)

    def track_line_and_color_track(self):
        thread1 = threading.Thread(target = self.save_film_and_color_track)
        thread1.setDaemon(True)
        thread1.start()

        self.track_line()
        self.camera.stop = True

        while thread1.is_alive():
            time.sleep(2)
    
    def track_line_and_test_camera_servo_control(self):
        thread1 = threading.Thread(target = self.camera.camera_servos.test_servo_control)
        thread1.setDaemon(True)
        thread1.start()

        self.track_line()

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
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    mark_lap = True
                    
                    if lap >= self.tracking_laps:
                        break
            elif mark_lap:
                mark_lap = False
                lap = lap + 1
            
            # Original conditions
            
            # Handle right acute angle and right right angle
            elif self.tracking_module.over_right_acute_angle_or_right_right_angle():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    # Turn right in place,speed is 100,delay 80ms
                    self.motors.sharp_right()
    
            # Handle left acute angle and left right angle 
            elif self.tracking_module.over_left_acute_angle_and_left_right_angle():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    # Turn right in place,speed is 100,delay 80ms  
                    self.motors.sharp_left()
    
            # Left_sensor1 detected black line
            elif self.tracking_module.left_sensor_1_detected_black_line():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    self.motors.spin_left()
        
            # Right_sensor2 detected black line
            elif self.tracking_module.right_sensor2_detected_black_line():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    self.motors.spin_right()
    
            elif self.tracking_module.middle_right_sensor_misses_black_line():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    self.motors.left()
    
            elif self.tracking_module.middle_left_sensor_misses_black_line():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    self.motors.right()

            elif self.tracking_module.both_middle_sensors_over_black_line():
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                    self.motors.run()
            else:
                # When the every sensor is NOT over the black line, the car keeps the previous running state.
                if self.tracking_module.current_tracking_option == LineTrackerModule.LineTrackingOptions.TRACK_LOST:
                    self.tracking_module.consecutive_tracking_option_times += 1
                   
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.track_lost_consecutive_times:
                        # # print consecutive_tracking_option_times
                        # print('\nconsecutive_tracking_option_times: ' + str(self.tracking_module.consecutive_tracking_option_times))
                        # # print track_lost_consecutive_times
                        # print('\ntrack_lost_consecutive_times: ' + str(self.tracking_module.track_lost_consecutive_times))

                        # print('\nTrack lost')
                        break
                else:
                    self.tracking_module.consecutive_tracking_option_times = 0
                    self.tracking_module.current_tracking_option = LineTrackerModule.LineTrackingOptions.TRACK_LOST
        
        self.motors.soft_stop()

    def color_track(self):
        t_start = time.time()
        times_to_be_consistent_trackable_color = 0

        lost_consecutive_times = 0

        try:
            while (not self.camera.stop) and time.time() < t_start + self.process_timeout:

                if not self.camera.processing_frame:
                    time.sleep(self.camera.last_frame_available_delay)
                    continue

                cnts = self.camera.get_color_countours(self.camera.processing_frame)

                cnts_len = len(cnts)
                # print('\nCountours: ' + str(cnts_len))

                if cnts_len <= 0:
                    times_to_be_consistent_trackable_color = 0

                    lost_consecutive_times += 1
                    if lost_consecutive_times >= self.camera.consistent_lost_consecutive_times:
                        if self.camera.camera_servos.move_in_current_direction(self.camera.degrees_to_move_to_track_color):
                            time.sleep(self.camera.delay_to_stop_after_moving)
                            self.camera.camera_servos.stop()
                            time.sleep(self.camera.delay_to_track_after_moving)
                    
                    continue
                
                color_x, color_y, color_width, color_height = self.camera.get_outer_coordinates(cnts)

                # print('\nColor x: ' + str(color_x) + ' y: ' + str(color_y) + ' width: ' + str(color_width) + ' height: ' + str(color_height))
                
                if self.debug:
                    # Mark the detected colors.
                    frame_copy = self.camera.processing_frame.copy()
                    self.camera.mark_the_detected_colors(frame_copy, color_x,color_y, color_width, color_height)
                    self.camera.display_frame(frame_copy)
                
                # Check if the detected color is large enough.
                if color_width < self.camera.min_color_width_to_track or color_height < self.camera.min_color_height_to_track:
                    times_to_be_consistent_trackable_color = 0
                    
                    lost_consecutive_times += 1
                    if lost_consecutive_times >= self.camera.consistent_lost_consecutive_times:
                        if self.camera.camera_servos.move_in_current_direction(self.camera.degrees_to_move_to_track_color):
                            time.sleep(self.camera.delay_to_stop_after_moving)
                            self.camera.camera_servos.stop()
                            time.sleep(self.camera.delay_to_track_after_moving)
                    
                    continue

                lost_consecutive_times = 0
                    
                # Consistent trackable color.
                if times_to_be_consistent_trackable_color < self.camera.servos_movement_times_delay:
                    time.sleep(self.camera.servos_movement_tracking_delay)
                    continue
                
                if self.camera.check_and_move_servos(color_x, color_y, color_width, color_height, self.camera.degrees_to_move_to_track_color):
                    time.sleep(self.camera.delay_to_stop_after_moving)
                    self.camera.camera_servos.stop()
                    time.sleep(self.camera.delay_to_track_after_moving)
                    continue

            self.camera.stop = True
        except Exception as e:
            print('\nError in color_track: ' + str(e))
            print('\n' + traceback.format_exc())

    def save_film(self):
        while not self.camera.stop:
            while self.camera.saving_frame_queue: 
                self.camera.result.write(self.camera.saving_frame_queue.get())
            time.sleep(self.camera.saving_frame_interval)

    def save_film_and_color_track(self):
        # print('\n Entered color_track method.')

        self.camera.camera_servos.init_servos_position()
        # self.camera.camera_servos.init_servos_position_gradually()

        # print('\nColor track start: ' + str(t_start))

        self.camera.init_film_capture()
        self.camera.init_film_saving()
        if self.debug:
            self.camera.init_film_display()

        thread1 = threading.Thread(target = self.save_film)
        thread1.setDaemon(True)
        thread1.start()

        thread2 = threading.Thread(target = self.color_track)
        thread2.setDaemon(True)
        thread2.start()

        # Read the first frame and stored as object property.
        while not self.camera.stop:
            ret, frame = self.camera.image.read()
            self.camera.saving_frame_queue.put(frame)
            self.camera.processing_frame = frame

        while thread1.is_alive():
            time.sleep(1)

        while thread2.is_alive():
            time.sleep(1)

        self.camera.finish_filming()

        return 0

    def chech_test_position(self, color_x, color_y, i):
        # print('\n¿Are you in the desired' + str(i) + ' test position? Y/N:N')

        in_position = input()

        if not in_position or in_position.upper == 'N':
            # print('\nMove to the desired' + str(i) + ' test position.')
            return i
        
        # print('\nWrite down X and Y value: X = ' + str(color_x) + ' Y = ' + str(color_y))

        return i + 1

        



                    
                    
