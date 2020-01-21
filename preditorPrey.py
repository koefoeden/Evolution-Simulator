from random import randint
from typing import List, Dict, Tuple, Sequence, NewType

import numpy as np

class Animal:
    def __init__(self, x_y: Tuple[int,int]):
        self._position = x_y

    def get_rand_adj_tile(self, dir_options: List[str]):
        #Generate random number:
        ran_num = randint(0, len(dir_options)-1)

        #Select random diection
        rand_dir = dir_options[ran_num]
        x, y = self._position

        chosen_tile= {
            "up": (x-1, y),
            "down": (x+1, y),
            "right": (x, y+1),
            "left": (x, y+1),
        }.get(rand_dir, (-1, -1))

        dir_options.remove(rand_dir)

        return chosen_tile, dir_options

    def move(self, x_y: Tuple[int, int]):
        self._position = x_y


class Mouse(Animal):
    ID = 0

    def __init__(self, x_y: Tuple[int, int]):
        super().__init__(x_y)
        alive = True
        time_since_offspring = 0
        self._ID_string = "M"+str(Mouse.ID)
        Mouse.ID += 1


class Owl(Animal):
    ID = 0

    def __init__(self, x_y: Tuple[int,int]):
        super().__init__(x_y)
        self._ID_string = "O"+str(Owl.ID)
        Owl.ID += 1


class Environment:

    def __init__(self, n, T, p, M, o):
        self._empty_field = '   '
        self._mice = []
        self._owls = []

        self._fields = [[self._empty_field for x in range(n)] for y in range(n)]
        self._mice_alive = 0

        self._ticks = T
        self._preg_time = p
        self._start_mice = M
        self._start_owls = o

    def print(self):
        #print(np.matrix(self._fields))
        #print('\n'.join([''.join(['{:4}'.format(item) for item in row])
        #                 for row in self._fields]))
        for row in self._fields:
            #print({}.__format__(row))
            print(row)

    def add_animal_at(self, animal: str, x_y: Tuple[int,int]):
        x, y = x_y
        if animal == "mouse":
            new_mouse = Mouse(x_y)
            self._mice += [new_mouse]
            self._fields[x][y] = "{:3}".format(new_mouse._ID_string)

        if animal == "owl":
            new_owl = Owl(x_y)
            self._owls += [new_owl]
            self._fields[x][y] = "{:3}".format(new_owl._ID_string)

    def is_legal_field(self, x_y: Tuple[int,int]):
        x, y = x_y
        try:
            return self._fields[x][y]==self._empty_field
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
                        if self._fields[x][y]=="M":
                            return x_y
                        else:
                            return internal_rec(remain_options)
                    except:
                        return internal_rec(remain_options)

        return internal_rec(["left", "up", "down", "right"])

    def animal_move_to(self, animal, x_y: Tuple[int, int]):
        #Clear field
        init_x, init_y = animal._position

        self._fields[init_x][init_y] = self._empty_field

        #Update field
        x, y = x_y
        self._fields[x][y] = animal._ID_string

    def owls_tick(self):
        for owl in self._owls:
            mouse_x_y = self.get_adj_tile_for(owl, "withMouse")
            if mouse_x_y != (-1, -1):
                self.animal_move_to(owl, mouse_x_y)
                
            else:
                near_x_y = self.get_adj_tile_for(owl, "randLegal")

                if near_x_y != (-1, -1):
                    self.animal_move_to(owl, near_x_y)

    def tick(self):
        self.owls_tick()

    def print_and_tick(self,no):
        for i in range (0, no):
            self.print()
            print("")
            self.tick()

if __name__ == '__main__':
    environment = Environment(5, 10, 2, 3, 2)
    environment.add_animal_at("mouse", (1, 1))
    environment.add_animal_at("owl", (4, 4))
    environment.add_animal_at("owl", (3, 3))
    environment.print_and_tick(10)
