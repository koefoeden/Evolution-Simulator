import environment
from variables import Variables

from random import randint, shuffle
from typing import Tuple
from termcolor import colored


class Animal:
    sex_dict = {0: "male", 1: "female"}

    def __init__(self, x_y: Tuple[int, int], parents, env):
        self.position = x_y
        self.is_pregnant = False
        self.is_pregnant_with = None
        self.time_pregnant = 0
        self.sex = Animal.sex_dict[randint(0, 1)]
        self.time_since_eaten = 0
        self.age = 0
        self.parents = parents
        self.color = None
        self.env = env
        self.has_moved = False
        self.adj_legal_tiles = self.get_adj_legal_tiles()

        # variables
        if parents and Variables.inherit_speed:
            self.speed = self.inherit("speed")
        else:
            self.speed = randint(1, 100)

    def __str__(self):
        if self.is_pregnant:
            return colored(str(self.speed).zfill(environment.Environment.empty_field_spaces - 1), self.color, attrs=['underline'])+" "
        else:
            return colored(str(self.speed).zfill(environment.Environment.empty_field_spaces - 1), self.color)+" "

    def inherit(self, trait):
        if trait == "speed":
            mean_parent_trait = (self.parents[0].speed+self.parents[1].speed)/2

        elif trait == "something else":
            mean_parent_trait = (self.parents[0].something_else+self.parents[1].something_else)/2

        rand_variance_int = randint(-Variables.rand_variance_trait, Variables.rand_variance_trait)
        rand_trait_contribution = (mean_parent_trait/100)*rand_variance_int

        return int(mean_parent_trait + rand_trait_contribution)

    def is_dead_action(self):
        if (self.time_since_eaten == self.die_of_hunger and self.die_of_hunger != 0) or \
                (self.age == self.max_age and self.max_age != 0):
            self.mark_as_dead()
            return True

    def get_adj_legal_tiles(self):
        x_pos, y_pos = self.position
        adj_coordinates = [(x_pos+x_move, y_pos+y_move) for x_move, y_move in Variables.dir_options]
        adj_legal_coordinates = [field for field in adj_coordinates if self.env.is_legal_field(field)]
        adj_legal_tiles = [self.env.fields[y][x] for (x, y) in adj_legal_coordinates if not self.env.fields[y][x].rock]
        shuffle(adj_legal_tiles)
        return adj_legal_tiles

    def get_owl_tiles(self):
        return [tile for tile in self.adj_legal_tiles if isinstance(tile.animal, Owl)]

    def get_male_owl_tiles(self):
        return [tile for tile in self.adj_legal_tiles if isinstance(tile.animal, Owl) and tile.animal.sex == "male"]

    def get_mouse_tiles(self):
        return [tile for tile in self.adj_legal_tiles if isinstance(tile.animal, Mouse)]

    def get_male_mouse_tiles(self):
        return [tile for tile in self.adj_legal_tiles if isinstance(tile.animal, Mouse) and tile.animal.sex == "male"]

    def get_empty_tiles(self):
        return [tile for tile in self.adj_legal_tiles if not tile.animal]

    def get_grass_tiles(self):
        return [tile for tile in self.adj_legal_tiles if tile.grass and (not tile.animal or tile.animal == self)]

    def get_move_tiles(self):
        return [tile for tile in self.adj_legal_tiles if not tile.animal or tile.animal == self]


class Mouse(Animal):
    ID = 0
    sex_color_dict = {'male': "blue", 'female': 'cyan'}

    def __init__(self, x_y: Tuple[int, int], parents, env=None):
        super().__init__(x_y, parents, env)
        self.ID = Mouse.ID
        Mouse.ID += 1
        self.color = Mouse.sex_color_dict[self.sex]

        # variables
        self.die_of_hunger = Variables.mouse_die_of_hunger
        self.preg_time = Variables.mouse_preg_time
        self.max_age = Variables.mouse_max_age

    def mark_as_dead(self):
        self.env.mice.remove(self)
        self.env.mice_alive -= 1
        self.env.clear_field(self)

    def action(self):
        if not self.has_moved:
            self.has_moved = True
            self.age += 1
            self.time_since_eaten += 1  #

            # Check for death conditions (death of age).
            if not self.is_dead_action():
                if self.is_pregnant:  # add pregnant time.
                    self.time_pregnant += 1

                self.adj_legal_tiles = self.get_adj_legal_tiles()
                empty_tiles = self.get_empty_tiles()

                # Owl near action
                if self.get_owl_tiles() and empty_tiles:
                    self.env.animal_move_to(self, empty_tiles[0])
                    return

                # eat grass action
                grass_tiles = self.get_grass_tiles()
                if grass_tiles:
                    self.env.animal_move_to(self, grass_tiles[0])
                    return

                    # Pregnancy action
                if empty_tiles and self.time_pregnant >= self.preg_time != 0:  # if time to baby
                    self.env.add_animal_at("mouse", empty_tiles[0], parents=[self, self.is_pregnant_with])
                    self.time_pregnant = 0
                    self.is_pregnant = False
                    self.is_pregnant_with = None
                    return

                # final move action
                move_tiles = self.get_move_tiles()
                if move_tiles:
                    self.env.animal_move_to(self, move_tiles[0])
                    return


class Owl(Animal):
    ID = 0
    sex_color_dict = {'male': "red", 'female': 'yellow'}

    def __init__(self, x_y: Tuple[int, int], parents, env=None):
        super().__init__(x_y, parents, env)
        self.ID = Owl.ID
        Owl.ID += 1
        self.color = Owl.sex_color_dict[self.sex]

        # variables
        self.die_of_hunger = Variables.owl_die_of_hunger
        self.preg_time = Variables.owl_preg_time
        self.max_age = Variables.owl_max_age

    def mark_as_dead(self):
        self.env.owls.remove(self)
        self.env.owls_alive -= 1
        self.env.clear_field(self)

    def is_birth_time_action(self, tiles):
        if self.time_pregnant >= self.preg_time != 0 and tiles:
            self.env.add_animal_at("owl", tiles[0])
            self.time_pregnant = 0
            self.is_pregnant = False
            self.is_pregnant_with = None
            return True

    def find_mouse_action(self):
        # hunt mice action
        mouse_tiles = self.get_mouse_tiles()
        if mouse_tiles:
            mouse_near = mouse_tiles[0].animal
            mouse_near_position = mouse_near.position

            # random catch ON
            if Variables.rand_catch:
                owl_to_mouse_speed_percentage = round(100*(self.speed/mouse_near.speed))
                rand_int = randint(1, 100)
                if rand_int <= owl_to_mouse_speed_percentage:
                    mouse_near.mark_as_dead()
                    self.time_since_eaten = 0
                    self.env.animal_move_to(self, mouse_tiles[0])
                    return True

                else:
                    mouse_near.action()
                    # if mouse_near.position == mouse_near_position:
                    if mouse_tiles[0].animal:
                        mouse_near.mark_as_dead()
                        self.time_since_eaten = 0
                    self.env.animal_move_to(self, mouse_tiles[0])
                    return True

            # random catch OFF
            elif not Variables.rand_catch:
                if mouse_near.speed <= self.speed:
                    mouse_near.mark_as_dead()
                    self.time_since_eaten = 0
                    self.env.animal_move_to(self, mouse_tiles[0])
                    return True

                else:
                    mouse_near.action()
                    if mouse_near.position == mouse_near_position:
                        mouse_near.mark_as_dead()
                        self.time_since_eaten = 0
                    self.env.animal_move_to(self, mouse_tiles[0])
                    return True

    def action(self):
        # self.has_moved = True
        self.time_since_eaten += 1
        self.age += 1

        if not self.is_dead_action():
            if self.is_pregnant:  # add pregnant time.
                self.time_pregnant += 1

            self.adj_legal_tiles = self.get_adj_legal_tiles()
            empty_tiles = self.get_empty_tiles()

            # birth action
            if not self.is_birth_time_action(empty_tiles):
                # find mouse action
                if not self.find_mouse_action():

                    # move action
                    move_tiles = self.get_empty_tiles()
                    if move_tiles:
                        self.env.animal_move_to(self, move_tiles[0])
