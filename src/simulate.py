from src import environment
import keyboard
import time
import cursor
from os import system
import configparser


########################
# CHOOSE A CONFIG FILE TO BE USED - OR MAKE YOUR OWN:
# cfg_file = 'config.ini'
# cfg_file = 'example_configs/mice_and_owls.ini'
# cfg_le = 'example_configs/only_mice.ini'
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
            elif keyboard.is_pressed('q'):
                environment.clear_screen()
                environment.restart_cursor()
                break
            if slow_mode:
                time.sleep(slow_mode_sleep_time)
