from random import randint, shuffle
from typing import List, Dict, Tuple, Sequence, NewType
import copy


class Animal:
    def __init__(self, x_y: Tuple[int, int]):
        self._position = x_y

    def get_rand_adj_tile(self, dir_options: List[str]):
        # Generate random number:
        ran_num = randint(0, len(dir_options) - 1)

        # Select random diection
        rand_dir = dir_options[ran_num]
        x, y = self._position

        chosen_tile = {
            "up": (x, y - 1),
            "down": (x, y + 1),
            "right": (x + 1, y),
            "left": (x - 1, y),
        }.get(rand_dir, (-1, -1))

        dir_options.remove(rand_dir)

        return chosen_tile, dir_options

    def move(self, x_y: Tuple[int, int]):
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

        self.add_animals()
        self.print_and_tick(self._ticks)

    def print(self):
        print("    ", end='')
        for i in range(self._n):
            print("{:^7}".format(i), end='')
        print()
        for i, row in enumerate(self._fields):
            print("{:^3}".format(i), end=' ')
            print(row)

    def add_animal_at(self, animal: str, x_y: Tuple[int, int]):
        x, y = x_y
        if animal == "mouse":
            new_mouse = Mouse(x_y)
            self._mice.insert(0, new_mouse)
            self._fields[y][x] = "{:3}".format(new_mouse._ID_string)

        if animal == "owl":
            new_owl = Owl(x_y)
            self._owls.insert(0, new_owl)
            self._fields[y][x] = "{:3}".format(new_owl._ID_string)

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        try:
            return (x >= 0) and (y >= 0) and self._fields[y][x] == self._empty_field
        except:
            return False

    def get_adj_tile_for(self, animal: Animal, tile_req: str):

        def internal_rec(dir_options):
            if dir_options == []:
                return -1, -1
            else:
                x_y, remain_options = animal.get_rand_adj_tile(dir_options)
                x, y = x_y

                if tile_req == "randLegal":
                    if self.is_legal_field(x_y):
                        return x_y
                    else:
                        return internal_rec(remain_options)

                elif tile_req == "withMouse":
                    try:
                        # add ID
                        if x >= 0 and y >= 0 and self._fields[y][x][0] == "M":
                            return x_y
                        else:
                            return internal_rec(remain_options)
                    except:
                        return internal_rec(remain_options)

        return internal_rec(["left", "up", "down", "right"])

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

    def add_animals(self):
        posibilities = [(x, y) for x in range(self._n) for y in range(self._n)]
        shuffle(posibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", posibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", posibilities[i2])


if __name__ == '__main__':
    environment = Environment(n=20, T=100, p=3, M=3, o=2)
