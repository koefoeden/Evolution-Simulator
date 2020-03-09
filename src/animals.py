import environment
from random import randint, shuffle
from typing import Tuple, List
from termcolor import colored


class Animal:
    sex_dict = {0: "male", 1: "female"}
    dir_options = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]

    def __init__(self, x_y: Tuple[int, int], parents: List, env):
        self.position = x_y
        self.is_pregnant = False
        self.is_pregnant_with = None
        self.time_pregnant = 0
        self.sex = Animal.sex_dict[randint(0, 1)]
        self.age = 0
        self.parents = parents
        self.color = None
        self.env = env
        self.has_moved = False
        self.adj_legal_tiles = self.get_adj_legal_tiles()

        # variables assigning - maybe redo?
        if isinstance(self, Mouse):
            self.die_of_hunger = int(self.env.config_parser['MICE']['m_die_of_hunger'])
            self.preg_time = int(self.env.config_parser['MICE']['m_preg_time'])
            self.max_age = int(self.env.config_parser['MICE']['m_max_age'])
        else:
            self.die_of_hunger = int(self.env.config_parser['OWLS']['o_die_of_hunger'])
            self.preg_time = int(self.env.config_parser['OWLS']['o_preg_time'])
            self.max_age = int(self.env.config_parser['OWLS']['o_max_age'])

        self.time_since_eaten = randint(0, self.die_of_hunger-1)

        # inheritance
        if parents and self.env.config_parser['INHERITANCE'].getboolean('speed'):
            self.speed = self.inherit_speed()
        else:
            self.speed = randint(1, 100)

    def string_speed(self):
        if environment.Environment.field_size < 5:
            if len(str(self.speed)) > environment.Environment.field_size:
                environment.Environment.field_size += 1
            return str(self.speed).zfill(environment.Environment.field_size)
        else:
            return '{:.0e}'.format(self.speed)

    def __str__(self):
        if self.is_pregnant:
            return colored(self.string_speed(), self.color, attrs=['underline'])
        else:
            return colored(self.string_speed(), self.color)

    def inherit_speed(self):
        mean_parent_trait = (self.parents[0].speed+self.parents[1].speed)/2
        rand_variance_int = randint(-self.env.rand_variance_trait, self.env.rand_variance_trait)
        rand_trait_contribution = (mean_parent_trait/100)*rand_variance_int

        return max(int(mean_parent_trait + rand_trait_contribution), 1)

    def is_dead_action(self):
        if (self.time_since_eaten == self.die_of_hunger and self.die_of_hunger != 0) or \
                (self.age == self.max_age and self.max_age != 0):
            self.mark_as_dead()
            return True

    def post_action(self):
        self.has_moved = True
        self.age += 1
        self.time_since_eaten += 1

    def get_adj_legal_tiles(self):
        x_pos, y_pos = self.position
        adj_coordinates = [(x_pos+x_move, y_pos+y_move) for x_move, y_move in Animal.dir_options]
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

    def mark_as_dead(self):
        pass


class Mouse(Animal):
    ID = 0
    sex_color_dict = {'male': "blue", 'female': 'cyan'}

    def __init__(self, x_y: Tuple[int, int], parents, env=None):
        super().__init__(x_y, parents, env)
        self.ID = Mouse.ID
        Mouse.ID += 1
        self.color = Mouse.sex_color_dict[self.sex]

    def mark_as_dead(self):
        self.env.mice.remove(self)
        self.env.mice_alive -= 1
        self.env.clear_field_of_animal(self)

    def action(self):
        if not self.has_moved:
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

                # Pregnancy action
                if empty_tiles and self.time_pregnant >= self.preg_time != 0:  # if time to baby
                    self.env.add_animal_at("mouse", empty_tiles[0], parents=[self, self.is_pregnant_with])
                    self.time_pregnant = 0
                    self.is_pregnant = False
                    self.is_pregnant_with = None
                    return

                # eat grass action
                grass_tiles = self.get_grass_tiles()
                if grass_tiles:
                    self.env.animal_move_to(self, grass_tiles[0])
                    return

                # final move action
                move_tiles = self.get_move_tiles()
                if move_tiles:
                    self.env.animal_move_to(self, move_tiles[0])
                    return


class Owl(Animal):
    ID = 0
    sex_color_dict = {'male': "red", 'female': 'yellow'}

    def __init__(self, x_y: Tuple[int, int], parents: List[object], env: [object] = None):
        super().__init__(x_y, parents, env)
        self.ID = Owl.ID
        Owl.ID += 1
        self.color = Owl.sex_color_dict[self.sex]

    def mark_as_dead(self):
        self.env.owls.remove(self)
        self.env.owls_alive -= 1
        self.env.clear_field_of_animal(self)

    def is_birth_time_action(self, tiles: List[object]):
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
            if self.env.rand_catch:
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
            elif not self.env.rand_catch:
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
        if not self.is_dead_action():
            if self.is_pregnant:  # add pregnant time.
                self.time_pregnant += 1

            self.adj_legal_tiles = self.get_adj_legal_tiles()
            empty_tiles = self.get_empty_tiles()

            if not self.is_birth_time_action(empty_tiles):
                # find mouse action
                if not self.find_mouse_action():
                    # move action
                    move_tiles = self.get_empty_tiles()
                    if move_tiles:
                        self.env.animal_move_to(self, move_tiles[0])
