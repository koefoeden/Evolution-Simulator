import environment
from variables import Variables
import keyboard

from os import system, name



if __name__ == '__main__':
    system('color')
    object_environment = environment.Environment(n=5, m=5, o=2)
    object_environment.print_initial_board()

    if Variables.keyboard_mode:
        while True:
            try:
                if keyboard.is_pressed('space'):
                    object_environment.tick_and_print()
                elif keyboard.is_pressed('q'):
                    system("cls")
                    print("\n")
                    print("\r")
                    break
            except:
                print("Unrecognized key")

    else:
        object_environment.tick_and_print_timed()
