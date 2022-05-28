#-*- coding:UTF-8 -*-
import sys

from model.Initializer import Initializer
from model.robot.RobotModule import Robot
from model.utils.RobotUtil import parse_arguments

def main(argv) -> int:
    parameter_list = parse_arguments(argv)
    
    initializer = Initializer()

    initializer.prepare_environment()

    robot = Robot(parameter_list)

    robot.play()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # next section explains the use of sys.exit