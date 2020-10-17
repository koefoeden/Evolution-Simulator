from unittest import TestCase
import animals
import environment
import configparser


class TestMarkAsDead(TestCase):
    def setUp(self):

        # Set up a test environment
        self.cfg_file = 'test_config.ini'
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.cfg_file)
        self.env = environment.Environment(self.config_parser)

    def test_mark_as_dead(self):
        self.env.mice[0].mark_as_dead()
        self.assertEqual(len(self.env.mice), self.env.start_mice-1)



