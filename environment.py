import animals

from random import shuffle
from typing import Tuple
import copy
from termcolor import colored
import time
from os import system, name


class Environment:
    empty_field_spaces = 4

    def __init__(self, n, T, p, M, o):
        self._empty_field = ' '*3
        self._n = n
        self._mice = []
        self._owls = []
        self._animals = []
        self._sleep_time = 2

        self._fields = [[self._empty_field for x in range(n)] for y in range(n)]
        self._mice_alive = 0
        self._owls_alive = 0

        self._ticks = T
        #self._preg_time = p
        self._start_mice = M
        self._start_owls = o

        self._dir_options_constant = [(0, 1), (1, 0), (0, -1), (-1, 0)]

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
            print()

    def add_animal_at(self, animal: str, x_y: Tuple[int, int], parents=None):
        x, y = x_y
        if animal == "mouse":
            new_mouse = animals.Mouse(x_y, parents)
            #self._mice.insert(0, new_mouse)
            self._animals.insert(0, new_mouse)
            self._fields[y][x] = new_mouse
            self._mice_alive += 1

        if animal == "owl":
            new_owl = animals.Owl(x_y, parents)
            #self._owls.insert(0, new_owl)
            self._animals.insert(0, new_owl)
            self._fields[y][x] = new_owl
            self._owls_alive += 1

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

    def get_ajd_legal_tile(self):
        pass

    def get_adj_mouse_tile(self):
        pass

    def get_adj_male_mouse_tile(self):
        pass

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

    def owls_tick(self):
        owls_copy = copy.copy(self._owls)

        for owl in owls_copy:
            if owl._alive:
                owl._time_since_eaten += 1

                if owl._time_since_eaten == animals.Owl._die_of_hunger:
                    owl._alive = False
                    self._owls_alive -= 1
                    self.clear_field(owl)
                    continue

                near_x_y = self.get_adj_tile_for(owl, "empty")

                if owl._is_pregnant:  # add pregnant time.
                    owl._time_pregnant += 1

                    if owl._time_pregnant >= animals.Owl._preg_time:  # if time to baby
                        if near_x_y != (-1, -1):
                            self.add_animal_at("owl", near_x_y)
                            owl._time_pregnant = 0
                            owl._is_pregnant = False
                            owl._is_pregnant_with = None
                            continue

                mouse_x_y = self.get_adj_tile_for(owl, "withMouse")
                if mouse_x_y != (-1, -1):
                    self.animal_move_to(owl, mouse_x_y)
                    owl._time_since_eaten = 0
                else:
                    self.animal_move_to(owl, near_x_y)

        # pregnancies
        for owl in owls_copy:
            if owl._alive and owl._sex == 'female' and not owl._is_pregnant:
                owl_near_x_y = self.get_adj_tile_for(owl, "withMaleOwl")

                if owl_near_x_y != (-1, -1):
                    owl._is_pregnant = True
                    owl._is_pregnant_with = owl_near_x_y

    def mice_tick(self):
        mice_copy = copy.copy(self._mice)
        mice_copy.sort(key=lambda mouse_elm: mouse_elm._speed)

        for mouse in mice_copy:  # loop through copy of mice list.
            if mouse._alive:  # only do something if mouse is alive.
                x, y = mouse._position

                if isinstance(self._fields[y][x], animals.Owl):  # if owl on tile, kill mouse.
                    mouse._alive = False
                    self._mice_alive -= 1

                else:  # action for alive mice.
                    if mouse._is_pregnant:  # add pregnant time.
                        mouse._time_pregnant += 1

                    near_x_y = self.get_adj_tile_for(mouse, "empty")
                    if near_x_y != (-1, -1):  # if a tile is free nearby
                        if mouse._time_pregnant >= animals.Mouse._preg_time:  # if time to baby
                            self.add_animal_at("mouse", near_x_y, parents=[mouse, mouse._is_pregnant_with])
                            mouse._time_pregnant = 0
                            mouse._is_pregnant = False
                            mouse._is_pregnant_with = None

                        else:
                            self.animal_move_to(mouse, near_x_y)

        # pregnancies.
        for mouse in mice_copy:
            if mouse._alive and mouse._sex == 'female' and not mouse._is_pregnant:
                mouse_near_x_y = self.get_adj_tile_for(mouse, "withMaleMouse")
                x, y = mouse_near_x_y

                if mouse_near_x_y != (-1, -1):
                    mouse._is_pregnant = True
                    mouse._is_pregnant_with = self._fields[y][x]

    def animals_tick(self):
        animals_copy = copy.copy(self._animals)
        animals_copy.sort(key=lambda animal_elm: animal_elm._speed, reverse=True)

        for animal in animals_copy:
            if animal._alive:
                x, y = animal._position

                # it is a mouse
                if isinstance(animal, animals.Mouse):
                    if isinstance(self._fields[y][x], animals.Owl):  # if owl on tile, kill mouse.
                        animal._alive = False
                        self._mice_alive -= 1
                        continue

                else:  # it is an owl
                    animal._time_since_eaten += 1

                    if animal._time_since_eaten == animals.Owl._die_of_hunger:
                        animal._alive = False
                        self._owls_alive -= 1
                        self.clear_field(animal)
                        continue

                if animal._is_pregnant:  # add pregnant time.
                    animal._time_pregnant += 1

                #get empty field
                near_x_y = self.get_adj_tile_for(animal, "empty")
                if near_x_y != (-1, -1):  # if a tile is free nearby
                    if animal._time_pregnant >= animals.Animal._preg_time:  # if time to baby
                        if isinstance(animal, animals.Mouse):
                            self.add_animal_at("mouse", near_x_y, parents=[animal, animal._is_pregnant_with])
                        else:
                            self.add_animal_at("owl", near_x_y, parents=[animal, animal._is_pregnant_with])
                        animal._time_pregnant = 0
                        animal._is_pregnant = False
                        animal._is_pregnant_with = None
                        continue

                # hunt mouse if owl
                if isinstance(animal, animals.Owl):
                    mouse_x_y = self.get_adj_tile_for(animal, "withMouse")
                    if mouse_x_y != (-1, -1):
                        self.animal_move_to(animal, mouse_x_y)
                        animal._time_since_eaten = 0
                        continue

                if near_x_y != (-1, -1):
                    self.animal_move_to(animal, near_x_y)

        # pregnancies.
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
        # self.owls_tick()
        # self.mice_tick()
        self.animals_tick()

    def average_speed_mice(self):
        total_speed = 0

        for mouse in self._mice:
            if mouse._alive:
                total_speed += mouse._speed
        if self._mice_alive > 0:
            return int(total_speed/self._mice_alive)
        else:
            return "N/A"

    def average_speed_owls(self):
        total_speed = 0

        for owl in self._owls:
            if owl._alive:
                total_speed += owl._speed
        if self._owls_alive > 0:
            return int(total_speed/self._owls_alive)
        else:
            return "N/A"

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

    def print_and_tick(self, no):
        system("cls")
        print(colored("Initial board", attrs=['underline', 'bold']))
        print()
        self.print()
        print()
        print("Mice: {:<5}  Avg. speed: {}".format(self._mice_alive, self.average_speed_mice()))
        print("Owls: {:<5}  Avg. speed: {}".format(self._owls_alive, self.average_speed_owls()))
        time.sleep(5*self._sleep_time)
        system("cls")
        for i in range(1, no+1):
            self.tick()
            print(colored("Tick: {}".format(i), attrs=['underline', 'bold']))
            print()
            self.print()
            print()
            print("Mice: {:<5}  Avg. speed: {}".format(self._mice_alive, self.average_speed()[0]))
            print("Owls: {:<5}  Avg. speed: {}".format(self._owls_alive, self.average_speed()[1]))
            time.sleep(self._sleep_time)
            system("cls")

    def add_animals(self):
        possibilities = [(x, y) for x in range(self._n) for y in range(self._n)]
        shuffle(possibilities)

        for i in range(self._start_mice):
            self.add_animal_at("mouse", possibilities[i])

        for i2 in range(self._start_mice, self._start_mice + self._start_owls):
            self.add_animal_at("owl", possibilities[i2])

