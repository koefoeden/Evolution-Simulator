import animals
from variables import Variables

from random import shuffle
from typing import Tuple
import copy
from termcolor import colored


def restart_cursor():
    print("\x1b[1;1H")


def clear_screen():
    print("\x1b[2J")


class Grass:
    def __str__(self):
        #return colored("".ljust(Environment.empty_field_spaces-1), on_color='on_green')+""
        return colored("MMM".ljust(Environment.empty_field_spaces-1), color='green')+" "

class Rock:
    def __str__self(self):
        return


class Environment:
    empty_field_spaces = 4

    def __init__(self, n, m, o, t=1000):
        self._ticks = t
        self._start_mice = m
        self._start_owls = o

        self._empty_field = ' '*3 + " "
        self._n = n
        self._mice = []
        self._owls = []
        self._tick_no = 0

        #new_grass = Grass()
        self._fields = [[Grass() for x in range(n)] for y in range(n)]
        self._mice_alive = 0
        self._owls_alive = 0

        # INITIALIZE
        self.add_animals()

    def add_animal_at(self, animal: str, x_y: Tuple[int, int], parents=None):
        x, y = x_y
        if animal == "mouse":
            new_mouse = animals.Mouse(x_y, parents, self)
            self._mice.append(new_mouse)
            self._fields[y][x] = new_mouse
            self._mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(x_y, parents, self)
            self._owls.append(new_owl)
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
        dir_options_call = copy.copy(Variables.dir_options)
        shuffle(dir_options_call)

        # Recursive function to try one direction at a time.
        def try_dir(dir_options_input):
            if dir_options_input == []: #base-case
                return None
            else:
                chosen_dir = dir_options_input.pop()
                candidate_tile = tuple(map(sum, zip(animal._position, chosen_dir)))
                x_cand, y_cand = candidate_tile

                if self.is_legal_field(candidate_tile):

                    if tile_req == "empty":
                        if self.is_empty_field(candidate_tile) or self._fields[y_cand][x_cand] == animal:
                            return candidate_tile

                    elif tile_req == "withMouse":
                        if isinstance(self._fields[y_cand][x_cand], animals.Mouse):
                            return candidate_tile

                    elif tile_req == "withOwl":
                        if isinstance(self._fields[y_cand][x_cand], animals.Owl):
                            return candidate_tile

                    elif tile_req == "run":
                        if self.is_empty_field(candidate_tile):
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
        self.clear_field(animal)
        animal._position = x_y
        x, y = x_y
        self._fields[y][x] = animal

    def clear_field(self, animal):
        x, y = animal._position
        self._fields[y][x] = self._empty_field

    def owls_tick(self):
        owls_copy = copy.copy(self._owls)
        shuffle(owls_copy)
        for owl in owls_copy:
            owl.action()

    def mice_tick(self):
        mice_copy = copy.copy(self._mice)
        #shuffle(mice_copy)
        mice_copy.sort(key=lambda animal_elm: animal_elm._speed, reverse=True)
        for mouse in mice_copy:
            if not mouse._has_moved:
                mouse.action()

    def update_pregnancies(self):
        for owl in self._owls:
            if owl._sex == 'female' and not owl._is_pregnant:
                male_near_x_y = self.get_adj_tile_for(owl, "withMaleOwl")
                if male_near_x_y:
                    x, y = male_near_x_y
                    owl._is_pregnant = True
                    owl._is_pregnant_with = self._fields[y][x]

        for mouse in self._mice:
            if mouse._sex == 'female' and not mouse._is_pregnant:
                male_near_x_y = self.get_adj_tile_for(mouse, "withMaleMouse")
                if male_near_x_y:
                    x, y = male_near_x_y
                    mouse._is_pregnant = True
                    mouse._is_pregnant_with = self._fields[y][x]

    def reset_moves(self):
        for mouse in self._mice:
            mouse._has_moved = False

        for owl in self._owls:
            owl._has_moved = False

    def tick(self):
        self.owls_tick()
        self.mice_tick()
        self.update_pregnancies()
        self.reset_moves()
        self._tick_no += 1

    def average_speed(self):
        total_speed_mice = 0
        total_speed_owls = 0

        for mouse in self._mice:
            total_speed_mice += mouse._speed

        for owl in self._owls:
            total_speed_owls += owl._speed

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
            print("{:^4}".format(i), end='')
        print()
        for i, row in enumerate(self._fields):
            print("{:^3}".format(i), end=' ')
            for item in row:
                print(str(item), end='')
            print()

    def print_info_and_board(self):
        print()
        self.print_board()
        print()
        print("Mice: {:<5}  Avg. speed: {}".format(self._mice_alive, self.average_speed()[0]))
        print("Owls: {:<5}  Avg. speed: {}".format(self._owls_alive, self.average_speed()[1]))

    def print_initial_tick(self):
        clear_screen()
        restart_cursor()
        print(colored("Initial board", attrs=['bold']))
        self.print_info_and_board()

    def tick_and_print(self):
        restart_cursor()
        self.tick()
        print(colored("Tick: {}         ".format(self._tick_no), attrs=['bold']))
        self.print_info_and_board()


