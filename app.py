import environment
from variables import Variables
import keyboard
import time
import cursor

from os import system, name



if __name__ == '__main__':
    system('color')
    #object_environment = environment.Environment(n=20, m=100, o=20)  # good with no owl replication, mouse pregtime 2.
    object_environment = environment.Environment(n=10, m=20, o=0)
    #object_environment = environment.Environment(n=15, m=90, o=15)
    object_environment.print_initial_tick()

    if Variables.keyboard_mode:
        slow_mode = True
        cursor.hide()
        while True:
            #try:
            if keyboard.is_pressed('space'):
                object_environment.tick_and_print()
            elif keyboard.is_pressed('Left'):
                slow_mode = True
            elif keyboard.is_pressed('Right'):
                slow_mode = False
            elif keyboard.is_pressed('l'):
                print(len(object_environment._mice))
            elif keyboard.is_pressed('q'):
                system("cls")
                print("\n")
                print("\r")
                break
            if slow_mode:
                time.sleep(Variables.slow_mode_sleep_time)

    else:
        object_environment.tick_and_print_timed()
