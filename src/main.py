#-*- coding:UTF-8 -*-
import sys

from model.Initializer import Initializer
from model.robot.Robot import Robot
from model.utils.Util import parse_arguments

def main(argv) -> int:
    parameter_list = parse_arguments(argv)
    
    initializer = Initializer()

    initializer.prepare_environment()

    robot = Robot()

    if not 'mode' in parameter_list:
        return 'Input a mode'

    robot.mode = parameter_list['mode']
    
    if 'desired_duty_cycle' in parameter_list:
        robot.motors.init_desired_duty_cycle(int(parameter_list['desired_duty_cycle']))
    
    if 'process_timeout' in parameter_list:
        robot.process_timeout = int(parameter_list['process_timeout'])
    
    if 'initial_delay' in parameter_list:
        robot.initial_delay = int(parameter_list['initial_delay'])

    if 'tracking_laps' in parameter_list:
        robot.tracking_laps = int(parameter_list['tracking_laps'])

    if 'color_to_track' in parameter_list:
        robot.camera.set_color_to_track(parameter_list['color_to_track'])

    if 'initial_x_servo_angle' in parameter_list:
        robot.camera.camera_servos.initial_x_servo_angle = int(parameter_list['initial_x_servo_angle'])
    
    if 'initial_y_servo_angle' in parameter_list:
        robot.camera.camera_servos.initial_y_servo_angle = int(parameter_list['initial_y_servo_angle'])

    robot.play()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # next section explains the use of sys.exit