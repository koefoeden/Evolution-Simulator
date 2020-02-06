import environment
from variables import Variables

from random import randint
from typing import Tuple
from termcolor import colored


class Animal:
    _sex_dict = {0: "male", 1: "female"}

    def __init__(self, x_y: Tuple[int, int], parents, env):
        self._position = x_y
        self._is_pregnant = False
        self._is_pregnant_with = None
        self._time_pregnant = 0
        self._sex = Animal._sex_dict[randint(0, 1)]
        self._time_since_eaten = 0
        self._age = 0
        self._parents = parents
        self._color = None
        self._env = env
        self._has_moved = False

        # variables
        if parents and Variables.inherit_speed:
            self._speed = self.inherit("speed")
        else:
            self._speed = randint(1, 100)

    def __str__(self):
        if self._is_pregnant:
            return colored(str(self._speed).zfill(environment.Environment.empty_field_spaces - 1), self._color, attrs=['underline'])+" "
        else:
            return colored(str(self._speed).zfill(environment.Environment.empty_field_spaces - 1), self._color)+" "

    def inherit(self, trait):
        if trait == "speed":
            mean_parent_trait = (self._parents[0]._speed+self._parents[1]._speed)/2

        elif trait == "something else":
            mean_parent_trait = (self._parents[0]._something_else+self._parents[1]._something_else)/2

        rand_variance_int = randint(-Variables.rand_variance_trait, Variables.rand_variance_trait)
        rand_trait_contribution = (mean_parent_trait/100)*rand_variance_int

        return int(mean_parent_trait + rand_trait_contribution)

    def is_dead_action(self):
        if (self._time_since_eaten == self._die_of_hunger and self._die_of_hunger != 0) or \
                (self._age == self._max_age and self._max_age != 0):
            self.mark_as_dead()
            return True


class Mouse(Animal):
    ID = 0
    _sex_color_dict = {'male': "blue", 'female': 'cyan'}

    def __init__(self, x_y: Tuple[int, int], parents, env=None):
        super().__init__(x_y, parents, env)
        self._ID = Mouse.ID
        Mouse.ID += 1
        self._color = Mouse._sex_color_dict[self._sex]

        # variables
        self._die_of_hunger = Variables.mouse_die_of_hunger
        self._preg_time = Variables.mouse_preg_time
        self._max_age = Variables.mouse_max_age

    def mark_as_dead(self):
        self._env._mice.remove(self)
        self._env._mice_alive -= 1
        self._env.clear_field(self)

    def action(self):
        self._has_moved = True
        x, y = self._position
        self._age += 1
        self._time_since_eaten += 1  # TODO: Implementation

        # Check for death conditions (death of age).
        if not self.is_dead_action():
            if self._is_pregnant:  # add pregnant time.
                self._time_pregnant += 1

            # check for nearby owl
            owl_x_y = self._env.get_adj_tile_for(self, "withOwl")
            if owl_x_y:
                run_x_y = self._env.get_adj_tile_for(self, "run")
                if run_x_y:
                    self._env.animal_move_to(self, run_x_y)
                return

            # Check for empty space nearby.
            near_x_y = self._env.get_adj_tile_for(self, "empty")
            if near_x_y and near_x_y != (x, y):
                if self._time_pregnant >= self._preg_time != 0:  # if time to baby
                    self._env.add_animal_at("mouse", near_x_y, parents=[self, self._is_pregnant_with])
                    self._time_pregnant = 0
                    self._is_pregnant = False
                    self._is_pregnant_with = None

                else:
                    self._env.animal_move_to(self, near_x_y)


class Owl(Animal):
    ID = 0
    _sex_color_dict = {'male': "red", 'female': 'yellow'}

    def __init__(self, x_y: Tuple[int, int], parents, env=None):
        super().__init__(x_y, parents, env)
        self._ID = Owl.ID
        Owl.ID += 1
        self._color = Owl._sex_color_dict[self._sex]

        # variables
        self._die_of_hunger = Variables.owl_die_of_hunger
        self._preg_time = Variables.owl_preg_time
        self._max_age = Variables.owl_max_age

    def mark_as_dead(self):
        self._env._owls.remove(self)
        self._env._owls_alive -= 1
        self._env.clear_field(self)


    def is_birth_time_action(self, x, y, near_x_y):
        if self._time_pregnant >= self._preg_time != 0 and near_x_y and near_x_y != (x, y):
            self._env.add_animal_at("owl", near_x_y)
            self._time_pregnant = 0
            self._is_pregnant = False
            self._is_pregnant_with = None
            return True

    def find_mouse_action(self):
        mouse_x_y = self._env.get_adj_tile_for(self, "withMouse")

        if mouse_x_y:
            x, y = mouse_x_y
            mouse_near = self._env._fields[y][x]

            if Variables.rand_catch:
                owl_to_mouse_speed_percentage = round(100*(self._speed/mouse_near._speed))
                rand_int = randint(1, 100)
                if rand_int <= owl_to_mouse_speed_percentage:
                    mouse_near.mark_as_dead()
                    self._time_since_eaten = 0
                    self._env.animal_move_to(self, mouse_x_y)
                    return True

                else:
                    mouse_near.action()
                    if mouse_near._position == mouse_x_y:
                        mouse_near.mark_as_dead()
                        self._time_since_eaten = 0
                    self._env.animal_move_to(self, mouse_x_y)
                    return True

            elif not Variables.rand_catch:
                if mouse_near._speed <= self._speed:
                    mouse_near.mark_as_dead()
                    self._time_since_eaten = 0
                    self._env.animal_move_to(self, mouse_x_y)
                    return True

                else:
                    mouse_near.action()
                    if mouse_near._position == mouse_x_y:
                        mouse_near.mark_as_dead()
                        self._time_since_eaten = 0
                    self._env.animal_move_to(self, mouse_x_y)
                    return True

    def action(self):
        self._has_moved = True
        x, y = self._position
        self._time_since_eaten += 1
        self._age += 1

        if not self.is_dead_action():
            if self._is_pregnant:  # add pregnant time.
                self._time_pregnant += 1

            near_x_y = self._env.get_adj_tile_for(self, "empty")
            if not self.is_birth_time_action(x, y, near_x_y):
                if not self.find_mouse_action():
                    self._env.animal_move_to(self, near_x_y)
