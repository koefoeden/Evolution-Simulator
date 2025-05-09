from __future__ import annotations
import animals as animals
import copy
from random import shuffle, randint
from typing import Tuple
from termcolor import colored
from os import system


def restart_cursor():
    print("\x1b[1;1H")


def clear_screen():
    print("\x1b[2J")


class Tile:
    def __init__(self, x: int, y: int, env: Environment):
        self.env = env
        self.position = (x, y)
        self.rock = False
        self.animal = None
        self.grass = False

        if env.in_medias_res:
            self.time_since_grass_eaten = randint(0, self.env.grass_grow_back)
        else:
            self.time_since_grass_eaten = 0

    def __str__(self):
        if self.rock:
            return colored("[" + "-"*(self.env.field_size - 2) + "]", color='white')
        elif self.animal and self.grass:
            return self.animal.__str__()
        elif self.animal and not self.grass:
            return self.animal.__str__()
        elif not self.animal and self.grass:
            return colored("M" * self.env.field_size, color='green')
        else:
            return ' ' * self.env.field_size


class Environment:
    sim_version = 1.00
    field_size = 3

    def __init__(self, config_parser):
        self.sim_version = Environment.sim_version
        self.field_size = Environment.field_size
        self.config_parser = config_parser
        self.start_mice = int(self.config_parser['MICE']['m_number'])
        self.start_owls = int(self.config_parser['OWLS']['o_number'])
        self.dimensions = int(self.config_parser['ENVIRONMENT']['dimensions'])
        self.grass_grow_back = int(self.config_parser['ENVIRONMENT']['grass_grow_back'])
        self.rock_chance = int(self.config_parser['ENVIRONMENT']['rock_chance'])
        self.in_medias_res = self.config_parser['MECHANICS'].getboolean('in_medias_res')
        self.rand_catch = self.config_parser['MECHANICS'].getboolean('rand_catch')
        self.rand_variance_trait = int(self.config_parser['INHERITANCE']['rand_variance_trait'])
        self.owls_target_slow_mice = self.config_parser['MECHANICS'].getboolean('owls_target_slow_mice')

        self.mice = []
        self.owls = []
        self.tick_no = 0
        self.step_no = 0

        self.tiles = [[Tile(x, y, self) for x in range(self.dimensions)] for y in range(self.dimensions)]
        self.mice_alive = 0
        self.owls_alive = 0

        # INITIALIZE
        self.add_animals()
        self.add_grass_and_rocks()

    def set_console_size(self):
        console_width = max(6*self.dimensions+8, 50)
        console_height = self.dimensions+20

        system(f'mode con: cols={console_width} lines={console_height}')

    def add_animal_at(self, animal: str, tile: Tile, parents=None):
        if animal == "mouse":
            new_mouse = animals.Mouse(tile.position, parents, self)
            self.mice.append(new_mouse)
            tile.animal = new_mouse
            tile.animal.grass = False  # TODO: hmm
            tile.animal.time_since_grass_eaten = 0
            self.mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(tile.position, parents, self)
            self.owls.append(new_owl)
            tile.animal = new_owl
            tile.animal.grass = False  # TODO: Hmm
            tile.animal.time_since_grass_eaten = 0
            self.owls_alive += 1

    def add_animals(self):
        tile_list = [self.tiles[y][x] for x in range(self.dimensions) for y in range(self.dimensions)]
        shuffle(tile_list)

        for i in range(self.start_mice):
            self.add_animal_at("mouse", tile_list[i])

        for i2 in range(self.start_mice, self.start_mice + self.start_owls):
            self.add_animal_at("owl", tile_list[i2])

    def add_grass_and_rocks(self):
        for row in self.tiles:
            for tile in row:
                if not tile.animal:
                    rand_int = randint(1, 100)
                    if rand_int <= self.rock_chance:
                        tile.rock = True
                    else:
                        if self.in_medias_res:
                            if tile.time_since_grass_eaten == self.grass_grow_back:
                                tile.grass = True
                        else:
                            tile.grass = True

    def is_legal_coordinates(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (0 <= x < self.dimensions) and (0 <= y < self.dimensions)

    def animal_move_to(self, animal: animals.Animal, dest_tile: Tile):
        self.clear_field_of_animal(animal)
        animal.position = dest_tile.position
        dest_tile.animal = animal
        if isinstance(animal, animals.Mouse):
            if dest_tile.grass:
                dest_tile.grass = False
                dest_tile.time_since_grass_eaten = 0
                animal.time_since_eaten = 0

    def clear_field_of_animal(self, animal: animals.Animal):
        x, y = animal.position
        self.tiles[y][x].animal = None

    def owls_tick(self, step_mode=False):
        owls_copy = copy.copy(self.owls)
        shuffle(owls_copy)
        for owl in owls_copy:
            if not owl.has_moved:
                owl.action()
                if step_mode:
                    self.print_board()
                    return True

    def mice_tick(self, step_mode=False):
        mice_copy = copy.copy(self.mice)
        mice_copy.sort(key=lambda animal_elm: animal_elm.speed, reverse=True)
        for mouse in mice_copy:
            if not mouse.has_moved:
                mouse.action()
                mouse.post_action()
                if step_mode:
                    self.print_board()
                    return True

    def update_pregnancies(self):
        for owl in self.owls:
            if owl.sex == 'female' and not owl.is_pregnant:
                male_tiles = owl.get_male_owl_tiles()
                if male_tiles:
                    owl.is_pregnant = True
                    owl.is_pregnant_with = male_tiles[0].animal

        for mouse in self.mice:
            if mouse.sex == 'female' and not mouse.is_pregnant:
                male_tiles = mouse.get_male_mouse_tiles()
                if male_tiles:
                    mouse.is_pregnant = True
                    mouse.is_pregnant_with = male_tiles[0].animal

    def reset_moves(self):
        for mouse in self.mice:
            mouse.has_moved = False

        for owl in self.owls:
            owl.has_moved = False

    def grow_grass(self):
        for row in self.tiles:
            for tile in row:
                if not tile.rock:
                    tile.time_since_grass_eaten += 1
                    if tile.time_since_grass_eaten > self.grass_grow_back:
                        tile.grass = True

    def tick(self):
        self.owls_tick()
        self.mice_tick()
        self.update_pregnancies()
        self.reset_moves()
        self.grow_grass()
        self.tick_no += 1
        self.step_no = 0

    def step(self):
        self.step_no += 1
        if not self.owls_tick(step_mode=True):
            if not self.mice_tick(step_mode=True):
                self.update_pregnancies()
                self.reset_moves()
                self.grow_grass()
                self.tick_no += 1
                self.step_no = 0
                self.print_board()

    def multiple_ticks(self, n):
        for i in range(n):
            self.tick()

    def average_speed(self):
        total_speed_mice = 0
        total_speed_owls = 0

        for mouse in self.mice:
            total_speed_mice += mouse.speed

        for owl in self.owls:
            total_speed_owls += owl.speed

        if self.mice_alive > 0:
            avg_speed_mice = int(total_speed_mice/self.mice_alive)
        else:
            avg_speed_mice = "N/A"

        if self.owls_alive > 0:
            avg_speed_owls = int(total_speed_owls/self.owls_alive)
        else:
            avg_speed_owls = "N/A"

        return [avg_speed_mice, avg_speed_owls]

    def print_board(self):
        print(" " + colored(f"Tick: {str(self.tick_no).ljust(5)}  Step: {str(self.step_no).ljust(3)}",
                            attrs=['underline']))
        print()
        print(" "*4, end='')
        for i in range(self.dimensions):
            print("{:^{}}".format(i+1, self.field_size), end=' ')
        print()
        for i, row in enumerate(self.tiles):
            print(" {:>2}".format(i+1), end=' ')
            for item in row:
                print(str(item), end=' ')
            print()
        print()

    def print_stats(self):
        print(" Mice: {:<5}  Avg. speed: {}".format(self.mice_alive, self.average_speed()[0]))
        print(" Owls: {:<5}  Avg. speed: {}".format(self.owls_alive, self.average_speed()[1]))
        print()

    def print_controls(self):
        print(' '+colored('Controls:', attrs=['underline']))
        print(" Space       -> Advance the simulation")
        print(" Right arrow -> Increase simulation speed")
        print(" Left arrow  -> Decrease simulation speed")
        print(" S           -> Enable step-mode")
        print(" T           -> enable tick-mode")
        print(" R           -> Restart simulation")
        print(" Q           -> Quit simulation")

    def print_board_and_stats(self):
        self.print_board()
        self.print_stats()

    def tick_and_print(self):
        restart_cursor()
        self.tick()
        self.print_board_and_stats()

    def step_and_print(self):
        restart_cursor()
        self.step()
        self.print_stats()

    def print_initial_board(self):
        self.set_console_size()
        clear_screen()
        restart_cursor()
        self.print_board_and_stats()
        self.print_controls()
