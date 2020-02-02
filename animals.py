import environment
from variables import Variables

from random import randint
from typing import Tuple
from termcolor import colored


class Animal:
    _sex_dict = {0: "male", 1: "female"}

    def __init__(self, x_y: Tuple[int, int], parents, environment_instance):
        self._position = x_y
        self._alive = True
        self._is_pregnant = False
        self._is_pregnant_with = None
        self._time_pregnant = 0
        self._sex = Animal._sex_dict[randint(0, 1)]
        self._age = 0
        self._time_since_eaten = 0
        self._time_alive = 0
        self._parents = parents
        self._color = None
        self._environment_instance = environment_instance

        # variables

        if parents and Variables.inherit_speed:
            self._speed = self.inherit("speed")
            """
            mean_parent_speed = (parents[0]._speed+parents[1]._speed)/2
            rand_variance_int = randint(-Variables.rand_variance_speed, Variables.rand_variance_speed)
            rand_speed_contribution = (mean_parent_speed/100)*rand_variance_int
            self._speed = int(mean_parent_speed + rand_speed_contribution)
            """
        else:
            self._speed = randint(1, 100)

    def __str__(self):
        if self._is_pregnant:
            return colored(str(self._speed).zfill(environment.Environment.empty_field_spaces - 1), self._color, attrs=['underline'])
        else:
            return colored(str(self._speed).zfill(environment.Environment.empty_field_spaces - 1), self._color)

    def inherit(self, trait):
        if trait == "speed":
            mean_parent_trait = (self._parents[0]._speed+self._parents[1]._speed)/2

        elif trait == "something else":
            mean_parent_trait = (self._parents[0]._something_else+self._parents[1]._something_else)/2

        rand_variance_int = randint(-Variables.rand_variance_trait, Variables.rand_variance_trait)
        rand_trait_contribution = (mean_parent_trait/100)*rand_variance_int

        return int(mean_parent_trait + rand_trait_contribution)


class Mouse(Animal):
    ID = 0
    _sex_color_dict = {'male': "blue", 'female': 'cyan'}

    def __init__(self, x_y: Tuple[int, int], parents, environment_instance=None):
        super().__init__(x_y, parents, environment_instance)
        self._ID = Mouse.ID
        Mouse.ID += 1
        self._color = Mouse._sex_color_dict[self._sex]

        # variables
        self._die_of_hunger = Variables.mouse_die_of_hunger
        self._preg_time = Variables.mouse_preg_time
        self._max_age = Variables.mouse_max_age

    def action(self):
        x, y = self._position

        if isinstance(self._environment_instance._fields[y][x], Owl):  # if owl on tile, kill mouse.
            self._alive = False
            self._environment_instance._mice_alive -= 1

        else:  # action for alive mice.
            if self._is_pregnant:  # add pregnant time.
                self._time_pregnant += 1

            near_x_y = self._environment_instance.get_adj_tile_for(self, "empty")
            if near_x_y != (-1, -1):  # if a tile is free nearby
                if self._time_pregnant >= self._preg_time:  # if time to baby
                    self._environment_instance.add_animal_at("mouse", near_x_y, parents=[self, self._is_pregnant_with])
                    self._time_pregnant = 0
                    self._is_pregnant = False
                    self._is_pregnant_with = None

                else:
                    self._environment_instance.animal_move_to(self, near_x_y)

class Owl(Animal):
    ID = 0
    _sex_color_dict = {'male': "red", 'female': 'yellow'}

    def __init__(self, x_y: Tuple[int, int], parents, environment_instance=None):
        super().__init__(x_y, parents, environment_instance)
        self._ID = Owl.ID
        Owl.ID += 1
        self._color = Owl._sex_color_dict[self._sex]

        # variables
        self._die_of_hunger = Variables.owl_die_of_hunger
        self._preg_time = Variables.owl_preg_time
        self._max_age = Variables.owl_max_age

    def action(self):
        self._time_since_eaten += 1

        if self._time_since_eaten == self._die_of_hunger:
            self._alive = False
            self._environment_instance._owls_alive -= 1
            self._environment_instance.clear_field(self)
            return

        else:
            near_x_y = self._environment_instance.get_adj_tile_for(self, "empty")

            if self._is_pregnant:  # add pregnant time.
                self._time_pregnant += 1

                if self._time_pregnant >= self._preg_time:  # if time to baby
                    if near_x_y != (-1, -1):
                        self._environment_instance.add_animal_at("owl", near_x_y)
                        self._time_pregnant = 0
                        self._is_pregnant = False
                        self._is_pregnant_with = None
                        return

            mouse_x_y = self._environment_instance.get_adj_tile_for(self, "withMouse")

            if mouse_x_y != (-1, -1):
                self._environment_instance.animal_move_to(self, mouse_x_y)
                self._time_since_eaten = 0
            else:
                self._environment_instance.animal_move_to(self, near_x_y)
