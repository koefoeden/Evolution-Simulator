class Variables:
    # moving
    dir_options = [(0, 1), (1, 0), (0, -1), (-1, 0), (0,0)]

    # mechanics:
    rand_catch = True

    # mice
    mouse_die_of_hunger = 0 # TODO: implement functionality
    mouse_preg_time = 2
    mouse_max_age = 0

    # owls
    owl_die_of_hunger = 4
    owl_preg_time = 15
    owl_max_age = 0

    # inheritance
    rand_variance_trait = 20
    inherit_die_of_hunger = False
    inherit_preg_time = False
    inherit_max_age = False
    inherit_speed = True


    # tick time:
    sleep_time = 0.5
    slow_mode_sleep_time = 0.1

    # keyboard mode
    keyboard_mode = True
