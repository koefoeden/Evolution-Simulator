from preditor_prey_revised import *


class Animal:
    _sex_dict = {0: "male", 1: "female"}

    def __init__(self, x_y: Tuple[int, int]):
        self._position = x_y
        self._alive = True
        self._is_pregnant = False
        self._is_pregnant_with = None
        self._time_pregnant = 0
        self._sex = Animal._sex_dict[randint(0, 1)]

        #variables
        self._speed = randint(1, 100)


class Mouse(Animal):
    ID = 0


    # variables
    _preg_time = 2
    _max_age = 10

    def __init__(self, x_y: Tuple[int, int]):
        super().__init__(x_y)
        self._ID = Mouse.ID
        self._age = 0
        Mouse.ID += 1

    def __str__(self):
        if self._sex == 'male':
            self._color = 'blue'
        else:
            self._color = 'cyan'
        if self._is_pregnant:
            string_rep = colored(str(self._speed).zfill(Environment.empty_field_spaces - 1), self._color, attrs=['underline'])
            return string_rep
        else:
            return colored(str(self._speed).zfill(Environment.empty_field_spaces-1), self._color)

    def print(self):
        if self._sex == 'male':
            self._color = 'blue'
        else:
            self._color = 'cyan'
        if self._is_pregnant:
            cprint(colored(str(self._speed).zfill(Environment.empty_field_spaces - 1), self._color, attrs=['bold', 'underline']), end='')
        else:
            cprint(colored(str(self._speed).zfill(Environment.empty_field_spaces-1), self._color), end='')


class Owl(Animal):
    ID = 0

    #variables
    _die_of_hunger = 3
    _max_age = 10
    _preg_time = 3

    def __init__(self, x_y: Tuple[int, int]):
        super().__init__(x_y)
        self._ID = Owl.ID
        Owl.ID += 1
        self._time_since_eaten =0

    def __str__(self):
        if self._is_pregnant:
            self._preg_string = 'P'
        else:
            self._preg_string = ''

        if self._sex == 'male':
            self._color = 'red'
        else:
            self._color = 'yellow'
        return colored(self._preg_string + str(self._speed).zfill(Environment.empty_field_spaces-1), self._color)

    def print(self):
        if self._sex == 'male':
            self._color = 'red'
        else:
            self._color = 'yellow'
        if self._is_pregnant:
            cprint(colored(str(self._speed).zfill(Environment.empty_field_spaces - 1), self._color, attrs=['bold', 'underline']), end='')
        else:
            cprint(colored(str(self._speed).zfill(Environment.empty_field_spaces-1), self._color), end='')