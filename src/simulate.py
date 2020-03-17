import environment
import keyboard
import time
import cursor
from os import system
import configparser
import sys


########################
# CHOOSE A CONFIG FILE TO BE USED WHEN FILE RUN DIRECTLY:
cfg_file = '../configs/interactive/my_config.ini'
########################


class Simulate:
    def __init__(self, cfg_file_string):
        self.cfg_file_string = cfg_file_string
        system('color')
        config_parser = configparser.ConfigParser()
        config_parser.read(cfg_file_string)
        slow_mode_sleep_time = float(config_parser['TICK_TIME']['slow_mode_sleep_time'])

        object_environment = environment.Environment(config_parser)
        object_environment.print_initial_tick()
        slow_mode = True
        cursor.hide()

        while True:
            if keyboard.is_pressed('space'):
                object_environment.tick_and_print()
            elif keyboard.is_pressed('Left'):
                slow_mode = True
            elif keyboard.is_pressed('Right'):
                slow_mode = False
            elif keyboard.is_pressed('r'):
                try:
                    Simulate(sys.argv[1])
                except IndexError:
                    Simulate(cfg_file)
                break
            elif keyboard.is_pressed('q'):
                break
            if slow_mode:
                time.sleep(slow_mode_sleep_time)


if __name__ == '__main__':
    try:
        Simulate(sys.argv[1])
    except IndexError:
        Simulate(cfg_file)
