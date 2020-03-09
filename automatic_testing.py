import environment
import configparser
import csv
import re
import os
import time

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

        """
        self.ticks = int(self.config_parser['AUTO_TESTING']['ticks'])
        self.repetitions = int(self.config_parser['AUTO_TESTING']['repetitions'])
        """

        # set config values
        self.config_dict = {}

        for section in self.config_parser.sections():
            self.config_dict[section] = {}
            for (var_name, val) in self.config_parser.items(section):
                print(section, var_name)
                if val not in ['True', 'False']:
                    self.config_dict[section][var_name] = self.get_config_values(self.config_parser[str(section)][str(var_name)])

        """
        self.m_die_of_hunger_values = self.get_config_values(self.config_parser['MICE']['m_die_of_hunger'])
        self.m_preg_time_values = self.get_config_values(self.config_parser['MICE']['m_preg_time'])
        self.m_number_values = self.get_config_values((self.config_parser['MICE']['m_number']))

        self.o_die_of_hunger_values = self.get_config_values(self.config_parser['OWLS']['o_die_of_hunger'])
        self.o_preg_time_values = self.get_config_values(self.config_parser['OWLS']['o_preg_time'])
        self.o_number_values = self.get_config_values((self.config_parser['OWLS']['o_number']))
        """

        self.create_results_file()

        self.num_of_configs = self.get_number_of_configs()
        if self.confirm_test_prompt():
            self.test_configs()

    def get_config_values(self, config_parser_string):
        match_instance = re.match(self.regex_range, config_parser_string)
        min_val = match_instance.group(1)
        max_val = match_instance.group(2)
        jump = match_instance.group(3)
        if jump:
            return list(range(int(min_val), int(max_val)+1, int(jump)))
        elif max_val:
            return list(range(int(min_val), int(max_val)+1))
        else:
            return [int(min_val)]

    def create_results_file(self):
        try:
            with open(results_file, 'x', newline='') as csv_file:
                header = []
                for section in self.config_parser.sections():
                    for (key, val) in self.config_parser.items(section):
                        header.append(key)
                header.remove('repetitions')
                header.extend(['avg_speed_mouse', 'avg_speed_owl'])

                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow(header)

        except FileExistsError:
            pass

    def get_number_of_configs(self):
        """
        num_of_configs = self.repetitions*len(self.m_die_of_hunger_values)*len(self.m_preg_time_values)\
                         * len(self.m_number_values)*len(self.o_die_of_hunger_values)*len(self.o_preg_time_values)\
                         * len(self.o_number_values)
        """
        num_of_configs = 1
        for section in self.config_dict.values():
            for value_list in section.values():
                num_of_configs *= len(value_list)

        return num_of_configs

    def confirm_test_prompt(self):
        time_single_run = self.test_configs(time_single_run=True)
        answer = input(f"You have selected {self.num_of_configs} configurations to be simulated. Based on a test of the first configuration to be simulated,"
                       f" this will take approximately {round(time_single_run*self.num_of_configs/60,2)} minutes to perform. Do you wish to continue? y/n:")
        return answer == 'y'

    def test_configs(self, time_single_run=False):
        if not time_single_run:
            print('Running simulation...')
        t0 = time.time()
        for i in range(self.config_dict['AUTO_TESTING']['repetitions'][0]):
            """
            for section_key, section_value in self.config_dict.items():
                for var_key, value_list in section_value.items():
                    for value in value_list:
                        self.config_parser.set(section_key, var_key, str(value))

        
                                            
        #for i in range(self.repetitions):
            for m_value_hunger in self.m_die_of_hunger_values:
                for m_value_preg_time in self.m_preg_time_values:
                    for m_value_number in self.m_number_values:
                        for o_value_hunger in self.o_die_of_hunger_values:
                            for o_value_preg_time in self.o_preg_time_values:
                                for o_value_number in self.o_number_values:
        """
            for m_value_hunger in self.config_dict['MICE']['m_die_of_hunger']:
                for m_value_preg_time in self.config_dict['MICE']['m_preg_time']:
                    for m_value_number in self.config_dict['MICE']['m_number']:
                        for o_value_hunger in self.config_dict['OWLS']['o_die_of_hunger']:
                            for o_value_preg_time in self.config_dict['OWLS']['o_preg_time']:
                                for o_value_number in self.config_dict['OWLS']['o_number']:

                                    self.config_parser.set("MICE", "m_die_of_hunger", str(m_value_hunger))
                                    self.config_parser.set("MICE", "m_preg_time", str(m_value_preg_time))
                                    self.config_parser.set("MICE", "m_number", str(m_value_number))
                                    self.config_parser.set("OWLS", "o_die_of_hunger", str(o_value_hunger))
                                    self.config_parser.set("OWLS", "o_preg_time", str(o_value_preg_time))
                                    self.config_parser.set("OWLS", "o_number", str(o_value_number))

                    # get specific configuration
                    row_data = []
                    for section in self.config_parser.sections():
                        for (key, val) in self.config_parser.items(section):
                            if not key == 'repetitions':
                                row_data.append(val)

                    # create environment and simulate number of ticks
                    object_environment = environment.Environment(self.config_parser)
                    object_environment.multiple_ticks(self.config_dict['AUTO_TESTING']['ticks'][0])

                    # add average speed to row data
                    row_data.extend(object_environment.average_speed())

                    # single test run
                    if time_single_run:
                        t1 = time.time()
                        return t1-t0

                    # write full row data into file
                    with open(results_file, 'a+', newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow(row_data)
        t1 = time.time()
        print(f'Testing completed in {round((t1-t0)/60,2)} minutes.')


if __name__ == '__main__':
    tester = Tester(cfg_file)
