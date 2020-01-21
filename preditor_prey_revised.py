from random import randint, shuffle
from typing import List, Dict, Tuple, Sequence, NewType
import copy
import time

class Animal:
    def __init__(self, x_y: Tuple[int, int]):
        self._position = x_y


class Mouse(Animal):
    ID = 0

    def __init__(self, x_y: Tuple[int, int]):
        super().__init__(x_y)
        self._alive = True
        self._time_since_offspring = 0
        self._ID_string = "M" + str(Mouse.ID)
        Mouse.ID += 1


class Owl(Animal):
    ID = 0

    def __init__(self, x_y: Tuple[int, int]):
        super().__init__(x_y)
        self._ID_string = "O" + str(Owl.ID)
        Owl.ID += 1


class Environment:
    def __init__(self, n, T, p, M, o):
        self._empty_field = '   '
        self._n = n
        self._mice = []
        self._owls = []

        self._fields = [[self._empty_field for x in range(n)] for y in range(n)]
        self._mice_alive = 0

        self._ticks = T
        self._preg_time = p
        self._start_mice = M
        self._start_owls = o

        self._dir_options = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        #RUN
        self.add_animals()
        self.print_and_tick(self._ticks)

    def print(self):
        string_builder = "   "
        for i in range(self._n):
            string_builder += "{:^7}".format(i)
        string_builder += "\n"

        for i, row in enumerate(self._fields):
            string_builder += "{:^3}".format(i)
            string_builder += str(row)
            string_builder += "\n"

        print(string_builder)
        ##old
        """
        print("    ", end='')
        for i in range(self._n):
            print("{:^7}".format(i), end='')
        print()
        for i, row in enumerate(self._fields):
            print("{:^3}".format(i), end=' ')
            print(row)
            """

    def add_animal_at(self, animal: str, x_y: Tuple[int, int]):
        x, y = x_y
        if animal == "mouse":
            new_mouse = Mouse(x_y)
            self._mice.insert(0, new_mouse)
            self._fields[y][x] = "{:3}".format(new_mouse._ID_string)
            self._mice_alive+=1

        if animal == "owl":
            new_owl = Owl(x_y)
            self._owls.insert(0, new_owl)
            self._fields[y][x] = "{:3}".format(new_owl._ID_string)

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (x >= 0) and (y >= 0) and (x < self._n) and (y < self._n)

    def is_empty_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return self._fields[y][x]==self._empty_field

    def get_adj_tile_for(self, animal: Animal, tile_req: str):
        # Initialize: Shuffling and copying
        dir_options = copy.copy(self._dir_options)
        shuffle(dir_options)

        x_y = animal._position

        # Recursive function to try one direction at a time.
        def try_dir(dir_options):
            if dir_options == []: #base-case
                return (-1,-1)
            else:
                chosen_dir = dir_options.pop()
                candidate_tile = tuple(map(sum, zip(animal._position, chosen_dir)))
                x_cand,y_cand = candidate_tile

                if self.is_legal_field(candidate_tile):

                    if tile_req == "randLegal":
                        if self.is_empty_field(candidate_tile):
                            return candidate_tile
                        else:
                            return try_dir(dir_options)

                    elif tile_req == "withMouse":
                        if self._fields[y_cand][x_cand][0] == "M":
                            return candidate_tile
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
        self._fields[y][x] = "{:3}".format(animal._ID_string)

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

        for mouse in mice_copy:
            if mouse._alive:
                x, y = mouse._position

                if self._fields[y][x][0] == 'O':
                    mouse._alive = False
                    self._mice_alive -= 1

                else:
                    mouse._time_since_offspring += 1

                    near_x_y = self.get_adj_tile_for(mouse, "randLegal")

                    if near_x_y != (-1, -1):
                        if mouse._time_since_offspring >= self._preg_time:
                            self.add_animal_at("mouse", near_x_y)
                            mouse._time_since_offspring = 0
                        else:
                            self.animal_move_to(mouse, near_x_y)

    def tick(self):
        self.owls_tick()
        self.mice_tick()

    def print_and_tick(self, no):
        for i in range(0, no):
            self.print()
            print("")
            self.tick()
            #time.sleep(1)
    #def print_animation(self):


    def add_animals(self):
        posibilities = [(x, y) for x in range(self._n) for y in range(self._n)]
        shuffle(posibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", posibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", posibilities[i2])


if __name__ == '__main__':
    environment = Environment(n=10, T=10, p=3, M=10, o=2)
    print(environment._mice_alive)
