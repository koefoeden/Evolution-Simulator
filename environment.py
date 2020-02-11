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
        self.position = (x, y)
        self.rock = False
        self.animal = None
        self.grass = False
        self.time_since_grass_eaten = 0

    def __str__(self):
        if self.rock:
            return colored("[-]", color='white') + " "
        elif self.animal and self.grass:
            return colored(self.animal.__str__())
        elif self.animal and not self.grass:
            return self.animal.__str__()
        elif not self.animal and self.grass:
            return colored("MMM", color='green') + " "
        else:
            return Environment.empty_field


class Environment:
    empty_field_spaces = 4
    empty_field = ' '*3 + " "

    def __init__(self):
        self.start_mice = Variables.mouse_number
        self.start_owls = Variables.owl_number

        self.n = Variables.dimensions
        self.mice = []
        self.owls = []
        self.tick_no = 0

        self.fields = [[Tile(x, y) for x in range(self.n)] for y in range(self.n)]
        self.mice_alive = 0
        self.owls_alive = 0

        # INITIALIZE
        self.add_animals()
        self.add_grass_and_rocks()

    def add_animal_at(self, animal: str, tile, parents=None):
        if animal == "mouse":
            new_mouse = animals.Mouse(tile.position, parents, self)
            self.mice.append(new_mouse)
            tile.animal = new_mouse
            tile.animal.grass = False
            tile.animal.time_since_grass_eaten = 0
            self.mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(tile.position, parents, self)
            self.owls.append(new_owl)
            tile.animal = new_owl
            tile.animal.grass = False
            tile.animal.time_since_grass_eaten = 0
            self.owls_alive += 1

    def add_animals(self):
        possibilities = [self.fields[y][x] for x in range(self.n) for y in range(self.n)]
        shuffle(possibilities)

        for i in range(self.start_mice):
            self.add_animal_at("mouse", possibilities[i])

        for i2 in range(self.start_mice, self.start_mice + self.start_owls):
            self.add_animal_at("owl", possibilities[i2])

    def add_grass_and_rocks(self):
        for row in self.fields:
            for tile in row:
                if not tile.animal:
                    rand_int = randint(1, 100)
                    if rand_int <= Variables.rock_chance:
                        tile.rock = True
                    else:
                        tile.grass = True

    def is_legal_field(self, x_y: Tuple[int, int]):
        x, y = x_y
        return (x >= 0) and (y >= 0) and (x < self.n) and (y < self.n)

    def animal_move_to(self, animal, tile):
        self.clear_field(animal)
        animal.position = tile.position
        tile.animal = animal
        if isinstance(animal, animals.Mouse):
            if tile.grass:
                tile.grass = False
                tile.time_since_grass_eaten = 0
                animal.time_since_eaten = 0

    def clear_field(self, animal):
        x, y = animal.position
        self.fields[y][x].animal = None

    def owls_tick(self):
        owls_copy = copy.copy(self.owls)
        shuffle(owls_copy)
        for owl in owls_copy:
            owl.action()

    def mice_tick(self):
        mice_copy = copy.copy(self.mice)
        mice_copy.sort(key=lambda animal_elm: animal_elm.speed, reverse=True)
        for mouse in mice_copy:
            if not mouse.has_moved:
                mouse.action()

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

        # for owl in self.owls:
        #     owl.has_moved = False

    def grow_grass(self):
        for row in self.fields:
            for tile in row:
                if not tile.rock:
                    tile.time_since_grass_eaten += 1
                    if tile.time_since_grass_eaten == Variables.grass_grow_back:
                        tile.grass = True

    def tick(self):
        self.owls_tick()
        self.mice_tick()
        self.update_pregnancies()
        self.reset_moves()
        self.grow_grass()
        self.tick_no += 1

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
        print("    ", end='')
        for i in range(self.n):
            print("{:^4}".format(i), end='')
        print()
        for i, row in enumerate(self.fields):
            print("{:^3}".format(i), end=' ')
            for item in row:
                print(str(item), end='')
            print()

    def print_info_and_board(self):
        print()
        self.print_board()
        print()
        print("Mice: {:<5}  Avg. speed: {}".format(self.mice_alive, self.average_speed()[0]))
        print("Owls: {:<5}  Avg. speed: {}".format(self.owls_alive, self.average_speed()[1]))

    def print_initial_tick(self):
        clear_screen()
        restart_cursor()
        print(colored("Initial board", attrs=['bold']))
        self.print_info_and_board()

    def tick_and_print(self):
        restart_cursor()
        self.tick()
        print(colored("Tick: {}         ".format(self.tick_no), attrs=['bold']))
        self.print_info_and_board()


