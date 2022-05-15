#-*- coding:UTF-8 -*-
import sys

from model.Initializer import Initializer
from model.robot.Robot import Robot




def main() -> int:
    initializer = Initializer()

    initializer.prepare_environment()

    robot = Robot()
    
    robot.track_line()

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit