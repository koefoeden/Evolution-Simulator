import environment
import configparser
import csv
import re

# owl configs
# owl_die_of_hunger_configs = [x for x in range(10, 11)]
# owl_preg_time_configs = [x for x in range(10, 11)]

# number of ticks for each simulation
ticks = 500

# number of repetitions of each configuration
repetitions = 5

########################
# CONFIG FILE TO BE USED
#cfg_file = "config_mice_example.ini"
cfg_file = 'config_automatic_testing.ini'
########################
# OUTPUT FILE
results_file = 'results5.csv'
########################


class Tester:
    def __init__(self, cfg_file_param):
        self.cfg_file = cfg_file_param
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.cfg_file)

        # get config values
        self.regex_range = r"([0-9]+)[^0-9]([0-9]+)[^0-9]([0-9]*)"
        self.die_of_hunger_values = self.get_values(self.config_parser['MICE']['die_of_hunger'])
        self.preg_time_values = self.get_values(self.config_parser['MICE']['preg_time'])
        #self.get_die_of_hunger_values()
        self.create_results_file()
        self.test_configs(repetitions)

    def get_values(self, config_parser_string):
        match_instance = re.match(self.regex_range, config_parser_string)
        min_val = int(match_instance.group(1))
        max_val = int(match_instance.group(2))
        jump = int(match_instance.group(3))
        return list(range(min_val, max_val, jump))

    def create_results_file(self):
        try:
            with open(results_file, 'x', newline='') as csv_file:
                header = []
                for section in self.config_parser.sections():
                    for (key, val) in self.config_parser.items(section):
                        header.append(key)
                header.extend(['avg_speed_mouse'])

                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow(header)
        except FileExistsError:
            pass

    def test_configs(self, no_of_reps):
        for i in range(no_of_reps):
            for value_hunger in self.die_of_hunger_values:
                for value_preg_time in self.preg_time_values:
                    self.config_parser.set("MICE", "die_of_hunger", str(value_hunger))
                    self.config_parser.set("MICE", "preg_time", str(value_preg_time))

                    # get specific configuration
                    row_data = []
                    for section in self.config_parser.sections():
                        for (key, val) in self.config_parser.items(section):
                            row_data.append(val)

                    # create environment and simulate number of ticks
                    object_environment = environment.Environment(self.config_parser)

                    # simulate
                    for i2 in range(ticks):
                        object_environment.tick()

                    # add average speed to row data
                    row_data.append(object_environment.average_speed()[0])

                    # write full row data into file
                    with open(results_file, 'a+', newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow(row_data)


if __name__ == '__main__':
    tester = Tester(cfg_file)


