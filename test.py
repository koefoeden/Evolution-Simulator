import sys
import time

def restart_line():
    sys.stdout.write('\r')
    sys.stdout.flush()



if __name__ == '__main__':

    """
    sys.stdout.write('some data')
    sys.stdout.flush()
    time.sleep(2)  # wait 2 seconds...
    restart_line()
    sys.stdout.write('other different data')
    sys.stdout.flush()
    """
    print("hey asdsad", end='')
    print('\r', end='')
    print("test", end='')
