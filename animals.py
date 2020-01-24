from preditor_prey_revised import *


class Animal:
    _sex_dict = {0: "male", 1: "female"}
    _rand_variance_max = 50
    _preg_time = 3

    def __init__(self, x_y: Tuple[int, int], parents):
        self._position = x_y
        self._alive = True
        self._is_pregnant = False
        self._is_pregnant_with = None
        self._time_pregnant = 0
        self._sex = Animal._sex_dict[randint(0, 1)]
        self._age = 0
        self._time_since_eaten = 0
        self._time_alive = 0
        self._parents = parents

        # variables

        if parents:
            mean_parent_speed = (parents[0]._speed+parents[1]._speed)/2
            rand_variance_int = randint(-Animal._rand_variance_max, Animal._rand_variance_max)
            rand_speed_contribution = (mean_parent_speed/100)*rand_variance_int
            self._speed = int(mean_parent_speed + rand_speed_contribution)
        else:
            self._speed = randint(1, 100)
    def __str__(self):
        if self._is_pregnant:
            return colored(str(self._speed).zfill(Environment.empty_field_spaces - 1), self._color, attrs=['underline'])
        else:
            return colored(str(self._speed).zfill(Environment.empty_field_spaces - 1), self._color)


class Mouse(Animal):
    ID = 0
    _sex_color_dict = {'male': "blue", 'female': 'cyan'}

    # variables
    _die_of_hunger = 3
    _preg_time = 2
    _max_age = 10

    def __init__(self, x_y: Tuple[int, int], parents):
        super().__init__(x_y, parents)
        self._ID = Mouse.ID
        Mouse.ID += 1
        self._color = Mouse._sex_color_dict[self._sex]

class Owl(Animal):
    ID = 0
    _sex_color_dict = {'male': "red", 'female': 'yellow'}

    #variables
    _die_of_hunger = 10
    _preg_time = 3
    _max_age = 10

    def __init__(self, x_y: Tuple[int, int], parents):
        super().__init__(x_y, parents)
        self._ID = Owl.ID
        Owl.ID += 1
        self._color = Owl._sex_color_dict[self._sex]

