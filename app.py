import environment
import keyboard
import time
import cursor
from os import system
import config as cfg
import configparser


########################
# CONFIG FILE TO BE USED
cfg_file = 'config.ini'
########################


if __name__ == '__main__':
    system('color')
    config_parser = configparser.ConfigParser()
    config_parser.read(cfg_file)
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
            time.sleep(cfg.slow_mode_sleep_time)
