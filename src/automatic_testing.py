from src import environment
import configparser
import csv
import re
import time

########################
# CONFIG FILE TO BE USED FOR SIMULATION
cfg_file = './auto_testing_config.ini'
########################
# OUTPUT FILE FOR SIMULATION RESULTS
# IF IT DOESN'T EXIST, A NEW ONE WILL BE CREATED. OTHERWISE DATA WILL BE APPENDED TO.
results_file = './results/automatic_testing.csv'
########################

class Tester:
    def __init__(self, cfg_file_param):
        self.cfg_file = cfg_file_param
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.cfg_file)
        self.regex_range = r"([0-9]+)[^0-9]*([0-9]*)[^0-9]*([0-9]*)"

        # set config values
        self.config_dict = {}

        # load configs into dict of values list
        for section in self.config_parser.sections():
            self.config_dict[section] = {}
            for (var_name, val) in self.config_parser.items(section):
                if val not in ['True', 'False']:
                    self.config_dict[section][var_name] = self.get_config_values(self.config_parser[str(section)][str(var_name)])

        self.create_results_file()

        self.num_of_configs = self.get_number_of_configs()

        # Ask for confirmation and run if positive
        if self.confirm_test_prompt():
            self.run_simulations()
        else:
            print('Simulation aborted.')

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
        num_of_configs = 1
        for section in self.config_dict.values():
            for value_list in section.values():
                num_of_configs *= len(value_list)

        return num_of_configs

    def confirm_test_prompt(self):
        num_of_simulations = self.num_of_configs*self.config_dict['AUTO_TESTING']['repetitions'][0]
        single_run_time = self.run_simulations(single_run=True)
        answer = input(f"You have selected {num_of_simulations}"
                       f" simulations to be run at {self.config_dict['AUTO_TESTING']['ticks'][0]} ticks each, based on"
                       f" {self.num_of_configs} different configurations. This will take approximately"
                       f" {round(single_run_time*num_of_simulations/60,2)} minutes to perform. Do you wish to continue? y/n:")
        return answer == 'y'

    def run_simulations(self, single_run=False):
        if not single_run:
            print('Running simulations... Can be stopped at any time.')

        t0 = time.time()

        for i in range(self.config_dict['AUTO_TESTING']['repetitions'][0]):

            for m_value_hunger in self.config_dict['MICE']['m_die_of_hunger']:
                self.config_parser.set("MICE", "m_die_of_hunger", str(m_value_hunger))

                for m_value_preg_time in self.config_dict['MICE']['m_preg_time']:
                    self.config_parser.set("MICE", "m_preg_time", str(m_value_preg_time))

                    for m_value_number in self.config_dict['MICE']['m_number']:
                        self.config_parser.set("MICE", "m_number", str(m_value_number))

                        for o_value_hunger in self.config_dict['OWLS']['o_die_of_hunger']:
                            self.config_parser.set("OWLS", "o_die_of_hunger", str(o_value_hunger))

                            for o_value_preg_time in self.config_dict['OWLS']['o_preg_time']:
                                self.config_parser.set("OWLS", "o_preg_time", str(o_value_preg_time))

                                for o_value_number in self.config_dict['OWLS']['o_number']:
                                    self.config_parser.set("OWLS", "o_number", str(o_value_number))

                                    # test config
                                    self.run_single_simulation()

                                    # single test run
                                    if single_run:
                                        t1 = time.time()
                                        return t1-t0

        full_simulation_time = time.time()
        print(f'Testing completed in {round((full_simulation_time - t0) / 60, 2)} minutes. '
              f'Results appended to {results_file}.')

    def run_single_simulation(self):
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

        # write full row data into file
        with open(results_file, 'a+', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(row_data)
