import animals
from variables import Variables

from random import shuffle
from typing import Tuple
import copy
from termcolor import colored
import time
from os import system, name


class Environment:
    empty_field_spaces = 4

    def __init__(self, n, m, o, t=1000):
        self._empty_field = ' '*3
        self._n = n
        self._mice = []
        self._owls = []
        self._animals = []
        self._sleep_time = Variables.sleep_time
        self._tick_no = 0

        self._fields = [[self._empty_field for x in range(n)] for y in range(n)]
        self._mice_alive = 0
        self._owls_alive = 0

        self._ticks = t
        self._start_mice = m
        self._start_owls = o

        self._dir_options_constant = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # INITIALIZE
        self.add_animals()

    def add_animal_at(self, animal: str, x_y: Tuple[int, int], parents=None):
        x, y = x_y
        if animal == "mouse":
            new_mouse = animals.Mouse(x_y, parents, self)
            #self._mice.insert(0, new_mouse)
            self._animals.insert(0, new_mouse)
            self._fields[y][x] = new_mouse
            self._mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(x_y, parents, self)
            #self._owls.insert(0, new_owl)
            self._animals.insert(0, new_owl)
            self._fields[y][x] = new_owl
            self._owls_alive += 1

    def add_animals(self):
        possibilities = [(x, y) for x in range(self._n) for y in range(self._n)]
        shuffle(possibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", possibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", possibilities[i2])

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (x >= 0) and (y >= 0) and (x < self._n) and (y < self._n)

    def is_empty_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return self._fields[y][x] == self._empty_field

    def get_adj_tile_for(self, animal, tile_req: str):
        # Initialize: Shuffling and copying
        dir_options_call = copy.copy(self._dir_options_constant)
        shuffle(dir_options_call)

        # Recursive function to try one direction at a time.
        def try_dir(dir_options_input):
            if dir_options_input == []: #base-case
                return (-1,-1)
            else:
                chosen_dir = dir_options_input.pop()
                candidate_tile = tuple(map(sum, zip(animal._position, chosen_dir)))
                x_cand, y_cand = candidate_tile

                if self.is_legal_field(candidate_tile):

                    if tile_req == "empty":
                        if self.is_empty_field(candidate_tile):
                            return candidate_tile

                    elif tile_req == "withMouse":
                        if isinstance(self._fields[y_cand][x_cand], animals.Mouse):
                            return candidate_tile

                    elif tile_req == "withMaleMouse":
                        if isinstance(self._fields[y_cand][x_cand], animals.Mouse):
                            if self._fields[y_cand][x_cand]._sex == "male":
                                return candidate_tile

                    elif tile_req == "withMaleOwl":
                        if isinstance(self._fields[y_cand][x_cand], animals.Owl):
                            if self._fields[y_cand][x_cand]._sex == "male":
                                return candidate_tile

                return try_dir(dir_options_input)

        return try_dir(dir_options_call)

    def animal_move_to(self, animal, x_y: Tuple[int, int]):
        # Clear field
        self.clear_field(animal)

        # Update animals coordinates
        animal._position = x_y

        # Update field
        x, y = x_y
        self._fields[y][x] = animal

    def clear_field(self, animal):
        x, y = animal._position
        self._fields[y][x] = self._empty_field

    def animals_tick(self):
        animals_copy = copy.copy(self._animals)
        animals_copy.sort(key=lambda animal_elm: animal_elm._speed, reverse=True)

        for animal in animals_copy:
            if animal._alive:
                animal.action()

        # pregnancies
        for animal in animals_copy:
            if animal._alive and animal._sex == 'female' and not animal._is_pregnant:
                if isinstance(animal, animals.Mouse):
                    male_near_x_y = self.get_adj_tile_for(animal, "withMaleMouse")
                else:
                    male_near_x_y = self.get_adj_tile_for(animal, "withMaleOwl")
                x, y = male_near_x_y

                if male_near_x_y != (-1, -1):
                    animal._is_pregnant = True
                    animal._is_pregnant_with = self._fields[y][x]

    def tick(self):
        self.animals_tick()
        self._tick_no += 1

    def average_speed(self):
        total_speed_mice = 0
        total_speed_owls = 0

        for animal in self._animals:
            if animal._alive:
                if isinstance(animal, animals.Mouse):
                    total_speed_mice += animal._speed
                else:
                    total_speed_owls += animal._speed
        if self._mice_alive > 0:
            avg_speed_mice = int(total_speed_mice/self._mice_alive)
        else:
            avg_speed_mice = "N/A"

        if self._owls_alive > 0:
            avg_speed_owls = int(total_speed_owls/self._owls_alive)
        else:
            avg_speed_owls = "N/A"

        return [avg_speed_mice, avg_speed_owls]

    def print_board(self):
        print("    ", end='')
        for i in range(self._n):
            print("{:^5}".format(i), end='')
        print()
        for i, row in enumerate(self._fields):
            print("{:^3}".format(i), end=' ')
            for item in row:
                print("["+str(item)+"]", end='')
            print()

    def print_info_and_board(self):
        print()
        self.print_board()
        print()
        print("Mice: {:<5}  Avg. speed: {}".format(self._mice_alive, self.average_speed()[0]))
        print("Owls: {:<5}  Avg. speed: {}".format(self._owls_alive, self.average_speed()[1]))

    def print_initial_tick(self):
        system("cls")
        print(colored("Initial board", attrs=['underline', 'bold']))
        self.print_info_and_board()

    def tick_and_print(self):
        system("cls")
        self.tick()
        print(colored("Tick: {}".format(self._tick_no), attrs=['underline', 'bold']))
        self.print_info_and_board()

    def tick_and_print_timed(self):
        for i in range(1, self._ticks):
            self.tick_and_print()
            time.sleep(self._sleep_time)
