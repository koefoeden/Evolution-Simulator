import animals
from variables import Variables

from random import shuffle, randint
from typing import Tuple
import copy
from termcolor import colored


def restart_cursor():
    print("\x1b[1;1H")


def clear_screen():
    print("\x1b[2J")


class Tile:
    def __init__(self, x, y):
        self._position = (x, y)
        self._rock = False
        self._animal = None
        self._grass = False
        self._time_since_grass_eaten = 0

    def __str__(self):
        if self._rock:
            return colored("[-]", color='white') + " "
        elif self._animal and self._grass:
            return colored(self._animal.__str__(), on_color='on_green')
        elif self._animal and not self._grass:
            return self._animal.__str__()
        elif not self._animal and self._grass:
            return colored("MMM", color='green') + " "
        else:
            return Environment._empty_field


class Environment:
    empty_field_spaces = 4
    _empty_field = ' '*3 + " "

    def __init__(self):
        self._start_mice = Variables.mouse_number
        self._start_owls = Variables.owl_number

        self._n = Variables.dimensions
        self._mice = []
        self._owls = []
        self._tick_no = 0

        self._fields = [[Tile(x, y) for x in range(self._n)] for y in range(self._n)]
        self._mice_alive = 0
        self._owls_alive = 0

        # INITIALIZE
        self.add_animals()
        self.add_grass_and_rocks()

    def add_animal_at(self, animal: str, tile, parents=None):
        if animal == "mouse":
            new_mouse = animals.Mouse(tile._position, parents, self)
            self._mice.append(new_mouse)
            tile._animal = new_mouse
            tile._animal._grass = False
            tile._animal._time_since_grass_eaten = 0
            self._mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(tile._position, parents, self)
            self._owls.append(new_owl)
            tile._animal = new_owl
            tile._animal._grass = False
            tile._animal._time_since_grass_eaten = 0
            self._owls_alive += 1

    def add_animals(self):
        possibilities = [self._fields[y][x] for x in range(self._n) for y in range(self._n)]
        shuffle(possibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", possibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", possibilities[i2])

    def add_grass_and_rocks(self):
        for row in self._fields:
            for tile in row:
                if not tile._animal:
                    rand_int = randint(1, 100)
                    if rand_int <= Variables.rock_chance:
                        tile._rock = True
                    else:
                        tile._grass = True

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (x >= 0) and (y >= 0) and (x < self._n) and (y < self._n)

    def animal_move_to(self, animal, tile):
        self.clear_field(animal)
        animal._position = tile._position
        tile._animal = animal
        if isinstance(animal, animals.Mouse):
            if tile._grass:
                tile._grass = False
                tile._time_since_grass_eaten = 0
                animal._time_since_eaten = 0

    def clear_field(self, animal):
        x, y = animal._position
        self._fields[y][x]._animal = None

    def owls_tick(self):
        owls_copy = copy.copy(self._owls)
        shuffle(owls_copy)
        for owl in owls_copy:
            owl.action()

    def mice_tick(self):
        mice_copy = copy.copy(self._mice)
        mice_copy.sort(key=lambda animal_elm: animal_elm._speed, reverse=True)
        for mouse in mice_copy:
            if not mouse._has_moved:
                mouse.action()

    def update_pregnancies(self):
        for owl in self._owls:
            if owl._sex == 'female' and not owl._is_pregnant:
                male_tiles = owl.get_male_owl_tiles()
                if male_tiles:
                    owl._is_pregnant = True
                    owl._is_pregnant_with = male_tiles[0]._animal

        for mouse in self._mice:
            if mouse._sex == 'female' and not mouse._is_pregnant:
                male_tiles = mouse.get_male_mouse_tiles()
                if male_tiles:
                    mouse._is_pregnant = True
                    mouse._is_pregnant_with = male_tiles[0]._animal

    def reset_moves(self):
        for mouse in self._mice:
            mouse._has_moved = False

        # for owl in self._owls:
        #     owl._has_moved = False

    def grow_grass(self):
        for row in self._fields:
            for tile in row:
                if not tile._rock:
                    tile._time_since_grass_eaten += 1
                    if tile._time_since_grass_eaten == Variables.grass_grow_back:
                        tile._grass = True

    def tick(self):
        self.owls_tick()
        self.mice_tick()
        self.update_pregnancies()
        self.reset_moves()
        self.grow_grass()
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


