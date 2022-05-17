#-*- coding:UTF-8 -*-
from enum import Enum
import sys

from model.Initializer import Initializer
from model.robot.Robot import Robot
from model.utils.Util import parse_arguments

class Mode(Enum):
    TRACK_LINE = 1
    FILM = 2
    COLOR_TRACK = 3
    TRACK_LINE_AND_COLOR_TRACK = 4

def main(argv) -> int:
    parameter_list = parse_arguments(argv)
    
    initializer = Initializer()

    initializer.prepare_environment()

    robot = Robot()

    if not 'mode' in parameter_list:
        return 'Input a mode'
    
    if 'desireddutycycle' in parameter_list:
        robot.motors.init_desired_duty_cycle(int(parameter_list['desireddutycycle']))
    
    if 'processtimeout' in parameter_list:
        robot.process_timeout = int(parameter_list['processtimeout'])

    if 'colortotrack' in parameter_list:
        robot.camera.set_color_to_track(parameter_list['colortotrack'])

    if parameter_list['mode'] == Mode.TRACK_LINE.name:
        robot.track_line()
    elif parameter_list['mode'] == Mode.FILM.name:
        robot.camera.film()
    elif parameter_list['mode'] == Mode.COLOR_TRACK.name:
        robot.camera.color_track()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # next section explains the use of sys.exit