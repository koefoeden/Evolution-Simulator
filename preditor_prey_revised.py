from animals import *
from random import randint, shuffle
from typing import List, Dict, Tuple, Sequence, NewType
import copy
from termcolor import colored, cprint
import time
#import sys
from os import system, name
import colorama



class Environment:
    empty_field_spaces = 4

    def __init__(self, n, T, p, M, o):
        self._empty_field = ' '*3
        self._n = n
        self._mice = []
        self._owls = []

        self._fields = [[self._empty_field for x in range(n)] for y in range(n)]
        self._mice_alive = 0

        self._ticks = T
        #self._preg_time = p
        self._start_mice = M
        self._start_owls = o

        self._dir_options = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        #RUN
        self.add_animals()
        self.print_and_tick(self._ticks)

    def print(self):
        print("    ", end='')
        for i in range(self._n):
            print("{:^5}".format(i), end='')
        print()
        for i, row in enumerate(self._fields):
            print("{:^3}".format(i), end=' ')
            for item in row:
                print("["+str(item)+"]", end='')
                """
                if item == self._empty_field:
                    print("[" + self._empty_field + "]", end='')
                else:
                    print("[", end='')
                    item.print()
                    print("]", end='')
                    """
            print()

    def add_animal_at(self, animal: str, x_y: Tuple[int, int]):
        x, y = x_y
        if animal == "mouse":
            new_mouse = Mouse(x_y)
            self._mice.insert(0, new_mouse)
            self._fields[y][x] = new_mouse
            self._mice_alive += 1

        if animal == "owl":
            new_owl = Owl(x_y)
            self._owls.insert(0, new_owl)
            self._fields[y][x] = new_owl

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (x >= 0) and (y >= 0) and (x < self._n) and (y < self._n)

    def is_empty_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return self._fields[y][x]==self._empty_field

    def get_adj_tile_for(self, animal, tile_req: str):
        # Initialize: Shuffling and copying
        dir_options = copy.copy(self._dir_options)
        shuffle(dir_options)

        # Recursive function to try one direction at a time.
        def try_dir(dir_options):
            if dir_options == []: #base-case
                return (-1,-1)
            else:
                chosen_dir = dir_options.pop()
                candidate_tile = tuple(map(sum, zip(animal._position, chosen_dir)))
                x_cand, y_cand = candidate_tile

                if self.is_legal_field(candidate_tile):

                    if tile_req == "randLegal":
                        if self.is_empty_field(candidate_tile):
                            return candidate_tile
                        else:
                            return try_dir(dir_options)

                    elif tile_req == "withMouse":
                        if isinstance(self._fields[y_cand][x_cand], Mouse):
                            return candidate_tile
                        else:
                            return try_dir(dir_options)

                    elif tile_req == "withMaleMouse":
                        if isinstance(self._fields[y_cand][x_cand], Mouse):
                            if self._fields[y_cand][x_cand]._sex == "male":
                                return candidate_tile
                            else:
                                return try_dir(dir_options)
                        else:
                            return try_dir(dir_options)
                else:
                    return try_dir(dir_options)

        return try_dir(dir_options)

    def animal_move_to(self, animal, x_y: Tuple[int, int]):
        # Clear field
        init_x, init_y = animal._position

        self._fields[init_y][init_x] = self._empty_field

        # Update animals coordinates
        animal._position = x_y

        # Update field
        x, y = x_y
        self._fields[y][x] = animal

    def owls_tick(self):
        for owl in self._owls:
            mouse_x_y = self.get_adj_tile_for(owl, "withMouse")
            if mouse_x_y != (-1, -1):
                self.animal_move_to(owl, mouse_x_y)

            else:
                near_x_y = self.get_adj_tile_for(owl, "randLegal")

                if near_x_y != (-1, -1):
                    self.animal_move_to(owl, near_x_y)

    def mice_tick(self):
        mice_copy = copy.copy(self._mice)

        for mouse in mice_copy:  # loop through copy of mice list.
            if mouse._alive:  # only do something if mouse is alive.
                x, y = mouse._position

                if isinstance(self._fields[y][x], Owl):  # if owl on tile, kill mouse.
                    mouse._alive = False
                    self._mice_alive -= 1

                else:  # action for alive mice.
                    if mouse._is_pregnant:  # add pregnant time.
                        mouse._time_pregnant += 1

                    near_x_y = self.get_adj_tile_for(mouse, "randLegal")
                    if near_x_y != (-1, -1):  # if a tile is free nearby
                        if mouse._time_pregnant >= Mouse._preg_time:  # if time to baby
                            self.add_animal_at("mouse", near_x_y)
                            mouse._time_pregnant = 0
                            mouse._is_pregnant = False
                            mouse._is_pregnant_with = None

                        else:
                            self.animal_move_to(mouse, near_x_y)

        # pregnancies.
        for mouse in mice_copy:
            if mouse._alive and mouse._sex == 'female' and not mouse._is_pregnant:
                mouse_near_x_y = self.get_adj_tile_for(mouse, "withMaleMouse")

                if mouse_near_x_y != (-1, -1):
                    mouse._is_pregnant = True
                    mouse._is_pregnant_with = mouse_near_x_y

    def tick(self):
        self.owls_tick()
        self.mice_tick()

    def print_and_tick(self, no):
        print(colored("Initial board", attrs=['underline', 'bold']))
        self.print()
        print()
        for i in range(1, no+1):
            self.tick()
            print(colored("Tick: {}".format(i), attrs=['underline', 'bold']))
            self.print()
            print("")
            time.sleep(0.5)
            system("cls")

    def add_animals(self):
        possibilities = [(x, y) for x in range(self._n) for y in range(self._n)]
        shuffle(possibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", possibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", possibilities[i2])


    def clear(self):
        if name == 'nt':
            _ = system('cls')

if __name__ == '__main__':
    #colorama.init()
    system('color')
    environment = Environment(n=10, T=200, p=3, M=10, o=3)
    #sys.stdout.flush()

    """
    for i in range(10):
        sys.stdout.write("\r{0}>".format("=" * i))
        sys.stdout.flush()
        time.sleep(0.5)
    
    """