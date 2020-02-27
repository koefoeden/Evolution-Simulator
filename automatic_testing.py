import environment
from os import system
import configparser
import csv
import time

# mice configs
mouse_die_of_hunger_configs = [x for x in range(1, 11)]
mouse_preg_time_configs = [x for x in range(1,11)]

# owl configs
owl_die_of_hunger_configs = [x for x in range(10)]
owl_preg_time_configs = [x for x in range(10)]

ticks = 1000
repetitions = 5

########################
# CONFIG FILE TO BE USED AS TEMPLATE
#cfg_file = "config_mice_example.ini"
cfg_file = 'config_automatic_testing.ini'
########################

if __name__ == '__main__':
    system('color')

    with open('results.csv', 'w', newline='') as csv_file:
        # read settings from config file
        config_parser = configparser.ConfigParser()
        config_parser.read(cfg_file)

        # get headers
        header = []
        for section in config_parser.sections():
            for (key, val) in config_parser.items(section):
                header.append(key)
        header.extend(['avg_speed_mouse', 'avg_speed_owl'])

        # write headers
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)

        # loop through different configurations
        for value_mouse_die_of_hunger in mouse_die_of_hunger_configs:
            config_parser.set("MICE", "die_of_hunger", str(value_mouse_die_of_hunger))
            for value_mouse_preg_time in mouse_preg_time_configs:
                config_parser.set("MICE", "preg_time", str(value_mouse_preg_time))
                row_data = []
                avg_speeds = []

                # get specific configuration
                for section in config_parser.sections():
                    for (key, val) in config_parser.items(section):
                        row_data.append(val)

                # create environment and simulate number of ticks
                for z in range(repetitions):
                    object_environment = environment.Environment(config_parser)
                    for i in range(ticks):
                        object_environment.tick()

                # calculate average speed and write it into result file
                avg_speeds.append(object_environment.average_speed()[0])
                filtered_avg_speeds = list(filter(lambda elm: elm != 'N/A', avg_speeds))
                if filtered_avg_speeds:
                    row_data.append(sum(filtered_avg_speeds)/len(filtered_avg_speeds))
                else:
                    row_data.append('N/A')

                writer.writerow(row_data)

