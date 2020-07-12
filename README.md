# Welcome to the Evolution Simulator!
This tool allows you to simulate the natural process of evolution in a simplified, artificial environment. Essentially, the tool simulates an environment filled with mice and owls. The mice strive to survive by eating grass, while the owls prey on the mice. Both animals are capable of propagating and pass down their genes to the offspring. Let evolution do its work, and see the marvelous effects of natural selection!

Every simulation is based on a number of settings that you will specify before beforehand - or you can choose a pre-determined configuration if you like!

The tool has two different modes:
1. Interactive mode, where you can see evolution working in real-time.
2. Simulation mode, where you can test a range of different custom configurations, figuring out which variables are important for stimulating evolution. 

Hope you enjoy the simulator.

Developed by Thomas Gade Koefoed 

## How to run:
1. Install the necessary packages listed in requirements.txt via PIP
2. Run src/app.py
3. Enjoy!

## Variables:
#### Environment
dimensions
rock_chance = 0
grass_grow_back = 1

[MECHANICS]
rand_catch = True
in_medias_res = True

[MICE]
m_number = 280
m_die_of_hunger = 0
m_preg_time = 2
m_max_age = 0

[OWLS]
o_number = 50
o_die_of_hunger = 5
o_preg_time = 3
o_max_age = 0

[INHERITANCE]
rand_variance_trait = 20
speed = True

[TICK_TIME]
slow_mode_sleep_time = 0.1
