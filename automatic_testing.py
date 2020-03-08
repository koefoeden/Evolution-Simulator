import environment
import configparser
import csv
import re
import os

########################
# CONFIG FILE TO BE USED FOR SIMULATION
cfg_file = 'config_automatic_testing.ini'
########################
# NAME OF OUTPUT FILE
results_file = 'results/data_new_analysis.csv'
########################

class Tester:
    def __init__(self, cfg_file_param):
        self.cfg_file = cfg_file_param
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.cfg_file)
        self.regex_range = r"([0-9]+)[^0-9]*([0-9]*)[^0-9]*([0-9]*)"

        self.ticks = int(self.config_parser['AUTO_TESTING']['ticks'])
        self.repetitions = int(self.config_parser['AUTO_TESTING']['repetitions'])

        # set config values
        self.m_die_of_hunger_values = self.get_values(self.config_parser['MICE']['m_die_of_hunger'])
        self.m_preg_time_values = self.get_values(self.config_parser['MICE']['m_preg_time'])
        self.o_die_of_hunger_values = self.get_values(self.config_parser['OWLS']['o_die_of_hunger'])
        self.o_preg_time_values = self.get_values(self.config_parser['OWLS']['o_preg_time'])

        self.create_results_file()
        self.test_configs()

    def get_values(self, config_parser_string):
        match_instance = re.match(self.regex_range, config_parser_string)
        min_val = match_instance.group(1)
        max_val = match_instance.group(2)
        jump = match_instance.group(3)
        if jump:
            return list(range(int(min_val), int(max_val), int(jump)))
        elif max_val:
            return list(range(int(min_val), int(max_val)))
        else:
            return [int(min_val)]

    def create_results_file(self):
        try:
            with open(results_file, 'x', newline='') as csv_file:
                header = []
                for section in self.config_parser.sections():
                    for (key, val) in self.config_parser.items(section):
                        header.append(key)
                header.extend(['avg_speed_mouse', 'ticks'])

                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow(header)

        except FileExistsError:
            pass

    def test_configs(self):
        for i in range(self.repetitions):
            for m_value_hunger in self.m_die_of_hunger_values:
                for m_value_preg_time in self.m_preg_time_values:
                    for o_value_hunger in self.o_die_of_hunger_values:
                        for o_value_preg_time in self.o_preg_time_values:
                            self.config_parser.set("MICE", "m_die_of_hunger", str(m_value_hunger))
                            self.config_parser.set("MICE", "m_preg_time", str(m_value_preg_time))
                            self.config_parser.set("OWLS", "o_die_of_hunger", str(o_value_hunger))
                            self.config_parser.set("OWLS", "o_preg_time", str(o_value_preg_time))

                            # get specific configuration
                            row_data = []
                            for section in self.config_parser.sections():
                                for (key, val) in self.config_parser.items(section):
                                    row_data.append(val)

                            # create environment and simulate number of ticks
                            object_environment = environment.Environment(self.config_parser)

                            # simulate
                            object_environment.multiple_ticks(self.ticks)

                            # add average speed to row data
                            row_data.extend([object_environment.average_speed()[0], self.ticks])

                            # write full row data into file
                            with open(results_file, 'a+', newline='') as csv_file:
                                writer = csv.writer(csv_file, delimiter=',')
                                writer.writerow(row_data)

if __name__ == '__main__':
    tester = Tester(cfg_file)
