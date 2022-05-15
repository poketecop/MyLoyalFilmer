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

    if 'desireddutycycle' in parameter_list:
        robot.motors.init_desired_duty_cycle(int(parameter_list['desireddutycycle']))
    
    robot.track_line()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # next section explains the use of sys.exit