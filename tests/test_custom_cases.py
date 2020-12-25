import unittest
from unittest import TestCase

import evolutionsimulator.environment as environment
import evolutionsimulator.animals as animals
import configparser




class CatchingMechanics(TestCase):
    def setUp(self) -> None:
        # Set up an empty test-environment.
        self.config_parser = configparser.ConfigParser()
        self.cfg_file = 'complex_case_1.ini'
        self.config_parser.read(self.cfg_file)
        self.env = environment.Environment(self.config_parser)

        # Test for empty, add animals and test for non-empty environment
        self.assertFalse(self.env.owls, "There should be no owls in the empty environment")
        self.assertFalse(self.env.mice, "There should be no mice in the empty environment")

        self.env.add_animal_at("mouse", self.env.tiles[3][3])
        self.env.add_animal_at("owl", self.env.tiles[3][4])

        self.assertTrue(self.env.owls, "There should be an an owl in the environment")
        self.assertTrue(self.env.mice, "There should be a mouse in the environment")

    def test_slow_mouse_fast_owl(self) -> None:
        # set speeds of animals and do one tick, seeing if mouse is dead:
        self.env.tiles[3][3].animal.speed = 25  # slow mouse
        self.env.tiles[3][4].animal.speed = 50  # fast owl

        self.env.tick()

        self.assertFalse(self.env.mice, "The single mice should have been killed")
        self.assertIsInstance(self.env.tiles[3][3].animal, animals.Owl, "The owl should have moved here.")

    def test_fast_mouse_slow_owl(self) -> None:
        # set speeds of animals and do one tick, seeing if mouse is dead:
        self.env.tiles[3][3].animal.speed = 50  # fast mouse
        self.env.tiles[3][4].animal.speed = 25  # slow owl

        self.env.tick()

        self.assertTrue(self.env.mice, "The single mice should have survived.")
        self.assertIsInstance(self.env.tiles[3][3].animal, animals.Owl, "The owl should have moved here.")

    def test_owl_behavior(self) -> None:
        pass


if __name__=="__main__":
    unittest.main()
