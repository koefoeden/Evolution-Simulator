![Image of app](https://imgur.com/8obpdcW.png)
# Welcome to the Evolution Simulator!
This tool allows you to simulate the natural process of evolution in a simplified, artificial environment. Essentially, the tool simulates an environment filled with mice and owls. The mice strive to survive by eating grass, while the owls prey on the mice. Both animals are capable of propagating and pass down their genes to the offspring. Let evolution do its work, and see the marvelous effects of natural selection!

Every simulation is based on a number of settings that you will specify before beforehand - or you can choose a pre-determined configuration if you like!

The tool has two different modes:
1. Interactive mode, where you can see evolution working in real-time.
2. Simulation mode, where you can test a range of different custom configurations, figuring out which variables are important for stimulating evolution.

In the environment, male and female mice are coloured dark and light blue respectively, while male and female owls are colored red and orange respectively. Each animal is given a number, indicating its level of speed. If the number is underlined, it means the animal is currently pregant, and will soon produce offspring.

## How to run:
1. Install the necessary packages listed in requirements.txt via PIP
2. Navigate to root folder and run "pythonw app.py" for smoothest experience
3. Follow instructions and enjoy!

## Variables:
#### Environment
* dimensions - number of vertical and horizontal tiles in the environment
* rock_chance - the probability in percent that a tile is an obstructive rock instead of grass
* grass_grow_back - number of ticks before grass grows back after being eaten

#### Simulation mechanics
* rand_catch - determines if catching is probability based or deterministic
* in_medias_res - determines if simulation is started cold or warm
* rand_variance_trait - the amount in percentage that offspring can vary in the speed trait from the average of its parents
* speed - determines whether or not the speed trait is inherited

#### Mice
* m_number - number of mice upon start of simulation
* m_die_of_hunger - number of ticks before a given mouse dies of hunger
* m_preg_time - number of ticks that a female mouse is pregnant
* m_max_age - number of ticks before a mouse dies of old age

#### Owls
* o_number
* o_die_of_hunger
* o_preg_time
* o_max_age

#### Tick_time (only for interactive mode)
* slow_mode_sleep_time - time between each tick when slow-mode is enabled

#### Auto_testing (only for simulation mode)
* ticks - number of ticks desired to be run for the simulation
* repetitions - number of repetitions to be run for each given configuration
