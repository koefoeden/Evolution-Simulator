import environment
from os import system
import configparser
import time

########################
# CONFIG FILE TO BE USED
cfg_file = 'config.ini'
########################

if __name__ == '__main__':
    system('color')
    config_parser = configparser.ConfigParser()
    config_parser.read(cfg_file)
    object_environment = environment.Environment(config_parser)
    for i in range(1000):
        object_environment.tick()
    object_environment.print_info_and_board()
