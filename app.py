import environment
import keyboard
import time
import cursor
from os import system
from variables import Variables


if __name__ == '__main__':
    system('color')
    object_environment = environment.Environment()
    object_environment.print_initial_tick()

    if Variables.keyboard_mode:
        slow_mode = True
        cursor.hide()
        while True:
            if keyboard.is_pressed('space'):
                object_environment.tick_and_print()
            elif keyboard.is_pressed('Left'):
                slow_mode = True
            elif keyboard.is_pressed('Right'):
                slow_mode = False
            elif keyboard.is_pressed('l'):
                print(len(object_environment.mice))
            elif keyboard.is_pressed('q'):
                system("cls")
                print("\n")
                print("\r")
                break
            if slow_mode:
                time.sleep(Variables.slow_mode_sleep_time)
