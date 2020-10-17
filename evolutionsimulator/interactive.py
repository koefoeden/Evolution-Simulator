import environment
import keyboard
import time
import cursor
from os import system
import configparser
import sys


########################
# CHOOSE A CONFIG FILE TO BE USED WHEN FILE RUN DIRECTLY:
cfg_file = 'configs/interactive/only_mice.ini'
########################


class InteractiveSimulator:
    def __init__(self, cfg_file_string):
        self.slow_mode = True
        self.step_mode = False
        self.env = None

        self.cfg_file_string = cfg_file_string

        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.cfg_file_string)
        self.slow_mode_sleep_time = float(self.config_parser['TICK_TIME']['slow_mode_sleep_time'])

        self.start_simulation()

    def start_simulation(self):
        self.env = environment.Environment(self.config_parser)
        self.env.print_initial_board()

        while True:
            if keyboard.is_pressed('space'):
                if not self.step_mode:
                    self.env.tick_and_print()
                else:
                    self.env.step_and_print()

            elif keyboard.is_pressed('Left'):
                self.slow_mode = True

            elif keyboard.is_pressed('Right'):
                self.slow_mode = False

            elif keyboard.is_pressed('r'):
                self.start_simulation()

            elif keyboard.is_pressed('s'):
                self.step_mode = True

            elif keyboard.is_pressed('t'):
                self.step_mode = False

            elif keyboard.is_pressed('q'):
                break

            if self.slow_mode:
                time.sleep(self.slow_mode_sleep_time)
            elif not self.slow_mode and self.step_mode:
                time.sleep(0.01)


if __name__ == '__main__':
    system('color')
    cursor.hide()
    try:
        InteractiveSimulator(sys.argv[1])
    except IndexError:
        print(f"Running simulation using {cfg_file}")
        InteractiveSimulator(cfg_file)
