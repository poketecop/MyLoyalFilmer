#-*- coding:UTF-8 -*-

from enum import Enum
import threading
import RPi.GPIO as GPIO
import time
from model.robot import CameraModule, RGBLighterModule
from model.robot import MotorsModule
from model.robot import LineTrackerModule
import traceback

DEFAULT_PROCESS_TIMEOUT = 10
DEFAULT_INITIAL_DELAY = 2
DEFAULT_RUN_DELAY = 0
DEFAULT_MIDDLE_DELAY = 0
DEFAULT_TRACKING_LAPS = 1
FINAL_DELAY = 5
LAP_DELAY = 0
WAIT_DELAY = 10
MIN_INITIAL_DELAY_NO_LAST_SECONDS = 2
DEFAULT_LAST_SECONDS = 3
DEFAULT_INSTRUCTIONS = "Run,5"

class Mode(Enum):
    TRACK_LINE = 1
    FILM = 2
    COLOR_TRACK = 3
    TRACK_LINE_AND_COLOR_TRACK = 4
    CALIBRATE_CAMERA_SERVOS = 5
    TEST_CAMERA_SERVO_CONTROL = 6
    TRACK_LINE_AND_TEST_CAMERA_SERVO_CONTROL = 7
    TEST_FPS = 8
    RUN_WITH_INSTRUCTIONS = 9
    RUN_WITH_INSTRUCTIONS_AND_COLOR_TRACK = 10
    INFINITE_TRACK_LINE_AND_COLOR_TRACK = 11
    INFINITE_COLOR_TRACK = 12
    TEST_TWO_CONSECUTIVE_FILMINGS = 13
    INFINITE_WAIT_TRACK_LINE_WAIT_REVERSE_TRACK_LINE = 14,
    INFINITE_TRACK_LINE = 15,
    
class Robot:

    motors = None
    camera = None
    tracking_module = None
    rgb_lighter = None
    process_timeout = None
    initial_delay = None
    last_seconds = None
    run_delay = None
    final_delay = None
    lap_delay = None
    wait_delay = None
    tracking_laps = None
    threading = None
    mode = None

    instructions = None
    reverse = None
    infinite = None

    tracking_finished = False

    def __init__(self, parameter_list, process_timeout = DEFAULT_PROCESS_TIMEOUT, initial_delay = DEFAULT_INITIAL_DELAY, run_delay = DEFAULT_RUN_DELAY, middle_delay = DEFAULT_MIDDLE_DELAY, last_seconds = DEFAULT_LAST_SECONDS, tracking_laps = DEFAULT_TRACKING_LAPS, mode = Mode.TRACK_LINE_AND_COLOR_TRACK.name, debug = False, final_delay = FINAL_DELAY, instructions = DEFAULT_INSTRUCTIONS, reverse = False, lap_delay = LAP_DELAY, wait_delay = WAIT_DELAY):
        if parameter_list:
            if 'mode' in parameter_list:
                mode = parameter_list['mode']
            
            if 'process_timeout' in parameter_list:
                process_timeout = parameter_list['process_timeout']
            
            if 'initial_delay' in parameter_list:
                initial_delay = parameter_list['initial_delay']

            if 'run_delay' in parameter_list:
                run_delay = parameter_list['run_delay']
            
            if 'middle_delay' in parameter_list:
                middle_delay = parameter_list['middle_delay']

            if 'last_seconds' in parameter_list:
                last_seconds = parameter_list['last_seconds']

            if 'tracking_laps' in parameter_list:
                tracking_laps = parameter_list['tracking_laps']

            if 'debug' in parameter_list:
                debug = parameter_list['debug'].lower() == 'yes'

            if 'final_delay' in parameter_list:
                final_delay = parameter_list['final_delay']
            
            if 'instructions' in parameter_list:
                instructions = parameter_list['instructions']
            
            if 'reverse' in parameter_list:
                reverse = parameter_list['reverse'].lower() == 'yes'
            
            if 'lap_delay' in parameter_list:
                lap_delay = parameter_list['lap_delay']
            
            if 'wait_delay' in parameter_list:
                wait_delay = parameter_list['wait_delay']

        self.init_pin_numbering_mode()

        self.motors = MotorsModule.Motors(parameter_list)
        self.tracking_module = LineTrackerModule.LineTracker(parameter_list)
        self.camera = CameraModule.Camera(parameter_list, process_timeout = process_timeout)
        self.rgb_lighter = RGBLighterModule.RGBLighter()
        
        self.process_timeout = int(process_timeout)
        self.initial_delay = float(initial_delay)
        self.run_delay = float(run_delay)
        self.middle_delay = float(middle_delay)
        self.last_seconds = float(last_seconds)
        self.tracking_laps = int(tracking_laps)
        self.mode = mode
        self.debug = debug
        self.final_delay = float(final_delay)
        self.lap_delay = float(lap_delay)
        self.wait_delay = int(wait_delay)
        self.instructions = instructions
        self.reverse = reverse

        self.infinite = False
        
    def play(self):
        try:
            if self.mode == Mode.TRACK_LINE.name:
                if self.reverse:
                    self.wait_and_reverse_track_line()
                else:
                    self.wait_and_track_line()
            elif self.mode == Mode.FILM.name:
                self.camera.film()
            elif self.mode == Mode.COLOR_TRACK.name:
                self.save_film_and_color_track()
            elif self.mode == Mode.TRACK_LINE_AND_COLOR_TRACK.name:
                self.track_line_and_color_track()
            elif self.mode == Mode.TEST_CAMERA_SERVO_CONTROL.name:
                self.camera.camera_servos.test_servo_control()
            elif self.mode == Mode.TRACK_LINE_AND_TEST_CAMERA_SERVO_CONTROL.name:
                self.track_line_and_test_camera_servo_control()
            elif self.mode == Mode.TEST_FPS.name:
                self.camera.test_fps()
            elif self.mode == Mode.RUN_WITH_INSTRUCTIONS.name:
                self.run_with_instructions(self.instructions)
            elif self.mode == Mode.RUN_WITH_INSTRUCTIONS_AND_COLOR_TRACK.name:
                self.run_with_instructions_and_color_track()
            elif self.mode == Mode.INFINITE_TRACK_LINE_AND_COLOR_TRACK.name:
                self.infinite_track_line_and_color_track()
            elif self.mode == Mode.INFINITE_COLOR_TRACK.name:
                self.infinite_save_film_and_color_track()
            elif self.mode == Mode.TEST_TWO_CONSECUTIVE_FILMINGS.name:
                self.camera.test_two_consecutive_filmings()
            elif self.mode == Mode.INFINITE_WAIT_TRACK_LINE_WAIT_REVERSE_TRACK_LINE.name:
                self.infinite_wait_track_line_wait_reverse_track_line()
            elif self.mode == Mode.INFINITE_TRACK_LINE.name:
                self.infinite_track_line()

            
        except Exception as error:
            print(error)
            print('\n\n' + traceback.format_exc())
        finally:
            print('\n*** Finish ***')
            GPIO.cleanup()
    
    def init_pin_numbering_mode(self):
        # Set the GPIO port to BCM encoding mode.
        GPIO.setmode(GPIO.BCM)

        # Ignore warning information
        GPIO.setwarnings(False)


    def infinite_save_film_and_color_track(self):
        self.infinite = True

        t_start = time.time()

        while time.time() < t_start + self.process_timeout:
            self.save_film_and_color_track()
            if not self.wait_delay:
                continue

            time.sleep(self.wait_delay)
        
    def infinite_track_line(self):
        self.infinite = True

        t_start = time.time()

        while time.time() < t_start + self.process_timeout:
            self.wait_and_track_line()
            if self.wait_delay:
                time.sleep(self.wait_delay)

            self.track_line()
            
    def infinite_track_line_and_color_track(self):
        self.infinite = True

        t_start = time.time()

        while time.time() < t_start + self.process_timeout:
            self.track_line_and_color_track()
            if not self.wait_delay:
                continue

            time.sleep(self.wait_delay)

    def track_line_and_color_track(self):
        thread1 = threading.Thread(target = self.save_film_and_color_track)
        thread1.setDaemon(True)
        thread1.start()

        if self.reverse:
            self.reverse_track_line()
        else:
            self.track_line()

        if self.final_delay:
            time.sleep(self.final_delay)
            
        # save_film_and_color_track thread communication.
        self.camera.stop = True

        while thread1.is_alive():
            time.sleep(2)
    
    def track_line_and_test_camera_servo_control(self):
        thread1 = threading.Thread(target = self.camera.camera_servos.test_servo_control)
        thread1.setDaemon(True)
        thread1.start()

        if self.reverse:
            self.reverse_track_line()
        else:
            self.track_line()

        while thread1.is_alive():
            time.sleep(2)
    
    def wait_and_track_line(self):
        self.initial_wait_and_notify_start()
        self.track_line()

    def return_to_simple_straight_line_start(self):
        exception = None

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        try:
            while time.time() < timeout_start + timeout:
                self.tracking_module.set_sensors_input_value()

                if not self.tracking_module.every_sensor_over_black():
                    break

                self.motors.run_with_lower_duty_cycle()
            
            aux_desired_duty_cycle = self.motors.desired_left_duty_cycle
            self.motors.set_lower_desired_duty_cycle()
            
            while time.time() < timeout_start + timeout:
                self.tracking_module.set_sensors_input_value()

                if self.tracking_module.both_middle_sensors_over_black_line():
                    self.motors.init_desired_duty_cycle(aux_desired_duty_cycle)
                    return

                self.adjust_to_line()

        except Exception as e:
            exception = e
            print('\nError in track_line: ' + str(e))
            print('\n' + traceback.format_exc())
        finally:
            self.motors.soft_stop()

            # Propagate the exception.
            if exception:
                raise exception
    
    def adjust_to_line(self):
        # The order of the following conditions is important
        # Handle right acute angle and right right angle
        if self.tracking_module.over_right_acute_angle_or_right_right_angle():
            if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_spin_consecutive_times:
                # Turn right in place,speed is 100,delay 80ms
                self.motors.sharp_right()

        # Handle left acute angle and left right angle 
        elif self.tracking_module.over_left_acute_angle_and_left_right_angle():
            if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_spin_consecutive_times:
                # Turn right in place,speed is 100,delay 80ms  
                self.motors.sharp_left()

        # Left_sensor detected black line
        elif self.tracking_module.left_sensor_detected_black_line():
            if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_spin_consecutive_times:
                self.motors.spin_left()
    
        # Right_sensor detected black line
        elif self.tracking_module.right_sensor_detected_black_line():
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
            # When the every sensor is NOT over the black line

            if self.tracking_module.current_tracking_option == LineTrackerModule.LineTrackingOptions.TRACK_LOST:
                self.tracking_module.consecutive_tracking_option_times += 1
            
                if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.track_lost_consecutive_times:
                    # print consecutive_tracking_option_times
                    print('\nconsecutive_tracking_option_times: ' + str(self.tracking_module.consecutive_tracking_option_times))
                    # print track_lost_consecutive_times
                    print('\ntrack_lost_consecutive_times: ' + str(self.tracking_module.track_lost_consecutive_times))

                    print('\nTrack lost')
                    
                    return False
            else:
                # The car keeps the previous running state.

                self.tracking_module.consecutive_tracking_option_times = 0
                self.tracking_module.current_tracking_option = LineTrackerModule.LineTrackingOptions.TRACK_LOST
                    
        return True

    def track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)

        # delay 2s	
        exception = None

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        lap = 0
        mark_lap = False
        mark_lap_times = 0
        consistent_mark_lap_times = 2

        try:
            
            # consecutive_tracking_option_times is managed in LineTrackerModule.py
            while time.time() < timeout_start + timeout:
                
                self.tracking_module.set_sensors_input_value()
                
                # 4 tracking pins level status
                # 0 0 0 0
                if self.tracking_module.every_sensor_over_black():
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_stop_consecutive_times:
                        
                        if not mark_lap:
                            mark_lap = True

                            lap = lap + 1

                            if self.lap_delay:
                                self.motors.soft_stop()
                                time.sleep(self.lap_delay)

                            if lap >= self.tracking_laps:
                                break

                            self.motors.run_with_lower_duty_cycle()
                else:
                    if mark_lap:
                        mark_lap_times = mark_lap_times + 1
                        
                        if mark_lap_times > consistent_mark_lap_times:
                            mark_lap = False
                
                    if (not self.adjust_to_line()):
                        break
                    
            # The car stops in a multiple horizontal black line so in order to start again in a future run
            # the car must return to the place where the line is a simple straight line
            self.return_to_simple_straight_line_start()
        except Exception as e:
            exception = e
            print('\nError in track_line: ' + str(e))
            print('\n' + traceback.format_exc())
        finally:
            if self.infinite:
                self.motors.soft_stop()
            else:
                self.motors.final_stop()
            # Propagate the exception.
            if exception:
                raise exception

    def reverse_track_line(self):
        # False means that sensor is over the black line
        # If the the sensor is over the black line, 
        # light is absorved by the black line and it doesn't return to sensor (False)
        # If the sensor is not over the black line, 
        # light is returned to the sensor (True)
        exception = None
        # delay 2s	

        timeout = self.process_timeout   # [seconds]

        timeout_start = time.time()

        lap = 0
        mark_lap = False
        lap_delayed = False

        try:
            while time.time() < timeout_start + timeout:
                self.tracking_module.set_sensors_input_value()

                self.motors.reverse_run_with_lower_duty_cycle()

                if not self.tracking_module.every_sensor_over_black():
                    break

            # consecutive_tracking_option_times is managed in LineTrackerModule.py
            while time.time() < timeout_start + timeout:
                
                self.tracking_module.set_sensors_input_value()
                
                # 4 tracking pins level status
                # 0 0 0 0
                if self.tracking_module.every_sensor_over_black():
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                        mark_lap = True
                        
                        if lap >= self.tracking_laps:
                            break

                        if lap > 0 and not lap_delayed:
                            if self.lap_delay:
                                self.motors.soft_stop()
                                time.sleep(self.lap_delay)
                                lap_delayed = True
                                self.motors.reverse_run_with_lower_duty_cycle()
                elif mark_lap:
                    mark_lap = False
                    lap = lap + 1
                    lap_delayed = False
                
                # Left_sensor detected black line
                elif self.tracking_module.reverse_left_sensor_detected_black_line():
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                        self.motors.reverse_left()

                # Right_sensor detected black line
                elif self.tracking_module.reverse_right_sensor_detected_black_line():
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                        self.motors.reverse_right()

                elif self.tracking_module.both_middle_sensors_over_black_line():
                    if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.consistent_consecutive_times:
                        self.motors.reverse_run()
                else:
                    
                    if self.tracking_module.current_tracking_option == LineTrackerModule.LineTrackingOptions.TRACK_LOST:
                        self.tracking_module.consecutive_tracking_option_times += 1

                        if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.reverse_consistent_track_lost_consecutive_times:
                            self.motors.reverse_run()
                    
                        if self.tracking_module.consecutive_tracking_option_times >= self.tracking_module.reverse_track_lost_consecutive_times:
                            # print consecutive_tracking_option_times
                            print('\nconsecutive_tracking_option_times: ' + str(self.tracking_module.consecutive_tracking_option_times))
                            # print reverse_track_lost_consecutive_times
                            print('\nreverse_track_lost_consecutive_times: ' + str(self.tracking_module.reverse_track_lost_consecutive_times))

                            print('\nTrack lost')
                            break
                    else:
                        self.tracking_module.consecutive_tracking_option_times = 0
                        self.tracking_module.current_tracking_option = LineTrackerModule.LineTrackingOptions.TRACK_LOST
            
        except Exception as e:
            exception = e
            print('\nError in track_line: ' + str(e))
            print('\n' + traceback.format_exc())
        finally:
            if self.infinite:
                self.motors.soft_stop()
            else:
                self.motors.final_stop()
            # Propagate the exception.
            if exception:
                raise exception

    def initial_wait_and_notify_start(self):
        self.wait_and_notify_start(self.initial_delay)

    def run_wait_and_notify_start(self):
        self.wait_and_notify_start(self.run_delay)

    def middle_wait_and_notify_start(self):
        self.wait_and_notify_start(self.middle_delay)

    def wait_and_notify_start(self, delay):
        if delay:
            if delay <= MIN_INITIAL_DELAY_NO_LAST_SECONDS:
                self.rgb_lighter.about_to_start()
                time.sleep(delay)
            else:
                time.sleep(delay - self.last_seconds)
                self.rgb_lighter.about_to_start()
                time.sleep(self.last_seconds)

    def wait_and_reverse_track_line(self):
        self.initial_wait_and_notify_start()
        self.reverse_track_line()
            
    def wait_track_line_wait_reverse_track_line(self):
        self.initial_wait_and_notify_start()
        self.run_wait_and_notify_start()
        self.track_line()
        self.middle_wait_and_notify_start()
        self.reverse_track_line()

    def infinite_wait_track_line_wait_reverse_track_line(self):
        self.infinite = True

        t_start = time.time()

        while time.time() < t_start + self.process_timeout:
            self.wait_track_line_wait_reverse_track_line()
            if not self.wait_delay:
                continue

            time.sleep(self.wait_delay)

    def color_track(self):
        t_start = time.time()
        print('\nColor track start: ' + str(t_start))

        times_to_be_consistent_trackable_color = 0

        lost_consecutive_times = 0

        color_tracked = False
        
        while self.camera.processing_frame is None and time.time() < t_start + self.process_timeout:
            time.sleep(self.camera.last_frame_available_delay)

        try:
            while (not self.camera.stop) and time.time() < t_start + self.process_timeout:
                cnts = self.camera.get_color_countours(self.camera.processing_frame)

                cnts_len = len(cnts)
                print('\nCountours: ' + str(cnts_len))

                if cnts_len <= 0:
                    times_to_be_consistent_trackable_color = 0

                    lost_consecutive_times += 1
                    if color_tracked:
                        if lost_consecutive_times >= self.camera.consistent_lost_consecutive_times:
                            if self.camera.camera_servos.move_in_current_direction(self.camera.degrees_to_move_to_track_color):
                                time.sleep(self.camera.delay_to_stop_after_moving)
                                self.camera.camera_servos.stop()
                                time.sleep(self.camera.delay_to_track_after_moving)
                    
                    continue
                
                color_x, color_y, color_width, color_height = self.camera.get_outer_coordinates(cnts)

                print('\nColor x: ' + str(color_x) + ' y: ' + str(color_y) + ' width: ' + str(color_width) + ' height: ' + str(color_height))
                
                if self.debug:
                    # Mark the detected colors.
                    frame_copy = self.camera.processing_frame.copy()
                    self.camera.mark_the_detected_colors(frame_copy, color_x,color_y, color_width, color_height)
                    self.camera.display_frame(frame_copy)
                
                # Check if the detected color is large enough.
                if color_width < self.camera.min_color_width_to_track or color_height < self.camera.min_color_height_to_track:
                    times_to_be_consistent_trackable_color = 0
                    
                    if color_tracked:
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
                    # One less time to be a consistent trackable color.
                    times_to_be_consistent_trackable_color += 1
                    time.sleep(self.camera.servos_movement_tracking_delay)
                    continue
                
                times_to_be_consistent_trackable_color = 0

                if self.camera.check_and_move_servos(color_x, color_y, color_width, color_height, self.camera.degrees_to_move_to_track_color):
                    color_tracked = True
                    time.sleep(self.camera.delay_to_stop_after_moving)
                    self.camera.camera_servos.stop()
                    time.sleep(self.camera.delay_to_track_after_moving)
                    continue

                time.sleep(self.camera.last_frame_available_delay)

            self.camera.stop = True

            print('\n Color track finish.')
        except Exception as e:
            print('\nError in color_track: ' + str(e))
            print('\n' + traceback.format_exc())

    def save_film_and_color_track(self):
        print('\n Entered color_track method.')

        self.camera.camera_servos.init_servos_position()
        # self.camera.camera_servos.init_servos_position_gradually()

        self.camera.init_film_capture()
        self.camera.init_film_saving()
        if self.debug:
            self.camera.init_film_display()

        thread1 = threading.Thread(target = self.camera.save_film)
        thread1.setDaemon(True)
        thread1.start()

        thread2 = threading.Thread(target = self.color_track)
        thread2.setDaemon(True)
        thread2.start()

        # Read the first frame and stored as object property.
        t_start = time.time()
        i = 0
        try:
            while not self.camera.stop:
                ret, frame = self.camera.image.read()
                self.camera.saving_frame_queue.append(frame)
                self.camera.processing_frame = frame
                i += 1
        except Exception as e:
            print('\nError in save_film_and_color_track: ' + str(e))
            print('\n' + traceback.format_exc())
        finally:
            self.camera.finish_film_capture()
            self.camera.video_capture_finished = True

            print('\nReading videoCapture finish.')
            print("\nFPS: " + str(i / (time.time() - t_start)))

            while thread1.is_alive():
                time.sleep(1)

            while thread2.is_alive():
                time.sleep(1)

            return 0

    def chech_test_position(self, color_x, color_y, i):
        print('\n¿Are you in the desired' + str(i) + ' test position? Y/N:N')

        in_position = input()

        if not in_position or in_position.upper == 'N':
            print('\nMove to the desired' + str(i) + ' test position.')
            return i
        
        print('\nWrite down X and Y value: X = ' + str(color_x) + ' Y = ' + str(color_y))

        return i + 1

    def run_with_instructions_and_color_track(self):
        
        thread1 = threading.Thread(target = self.save_film_and_color_track)
        thread1.setDaemon(True)
        thread1.start()

        self.run_with_instructions(self.instructions)

        if self.final_delay:
            time.sleep(self.final_delay)

        self.camera.stop = True

        while thread1.is_alive():
            time.sleep(1)

        return 0

    def run_with_instructions(self, instructions):
        '''With an input string as parameter containing instructions with action, time and desired duty cycle (this is optional),
        use Motors Action enum to call related Motors class methods (methods with the same names as enum names) and wait the time set in the instuction.
        '''

        print('\n Entered motors_action method.')

        instructions_list = instructions.split(';')
        for instruction in instructions_list:
            instruction_list = instruction.split(',')
            action = instruction_list[0]

            if len(instruction_list) > 1:
                instrucion_time = float(instruction_list[1])
            else:
                instrucion_time = None

            if len(instruction_list) > 2:
                duty_cycle = int(instruction_list[2])
            else:
                duty_cycle = None

            print('\nAction: ' + action + ' time: ' + str(instrucion_time) + ' duty_cycle: ' + str(duty_cycle))

            if action.upper() == MotorsModule.Action.RUN.name:
                if duty_cycle:
                    self.motors.run_with_duty_cycle(duty_cycle, duty_cycle)
                else:
                    self.motors.run()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.STOP.name:
                self.motors.soft_stop()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.LEFT.name:
                if duty_cycle:
                    self.motors.left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.left()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.RIGHT.name:
                if duty_cycle:
                    self.motors.right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.right()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.SPIN_LEFT.name:
                if duty_cycle:
                    self.motors.spin_left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.spin_left()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.SPIN_RIGHT.name:
                if duty_cycle:
                    self.motors.spin_right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.spin_right()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.SHARP_LEFT.name:
                if duty_cycle:
                    self.motors.sharp_left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.sharp_left()
                if instrucion_time:
                    time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.SHARP_RIGHT.name:
                if duty_cycle:
                    self.motors.sharp_right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.sharp_right()
                if instrucion_time:
                    time.sleep(instrucion_time)
            # Reverse
            elif action.upper() == MotorsModule.Action.REVERSE_RUN.name:
                if duty_cycle:
                    self.motors.reverse_run_with_duty_cycle(duty_cycle, duty_cycle)
                else:
                    self.motors.reverse_run()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_LEFT.name:
                if duty_cycle:
                    self.motors.reverse_left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_left()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_RIGHT.name:
                if duty_cycle:
                    self.motors.reverse_right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_right()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_SPIN_LEFT.name:
                if duty_cycle:
                    self.motors.reverse_spin_left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_spin_left()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_SPIN_RIGHT.name:
                if duty_cycle:
                    self.motors.reverse_spin_right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_spin_right()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_SHARP_LEFT.name:
                if duty_cycle:
                    self.motors.reverse_sharp_left_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_sharp_left()
                time.sleep(instrucion_time)
            elif action.upper() == MotorsModule.Action.REVERSE_SHARP_RIGHT.name:
                if duty_cycle:
                    self.motors.reverse_sharp_right_with_duty_cycle(duty_cycle)
                else:
                    self.motors.reverse_sharp_right()
                time.sleep(instrucion_time)
            else:
                print('\nAction not recognized.')

        self.motors.soft_final_stop()
                

        



                    
                    
