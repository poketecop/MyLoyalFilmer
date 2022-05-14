#-*- coding:UTF-8 -*-
import sys

from es.uned.tfg.myloyalfilmer.model.Initializer import Initializer
from es.uned.tfg.myloyalfilmer.model.robot.Robot import Robot

def main() -> int:
    initializer = Initializer()

    initializer.prepare_environment()

    robot = Robot()
    
    robot.track_line()

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit