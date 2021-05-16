import sys
import select
import tty
import termios

# input is whatever device file was given by command-line argument
def get_binary_bongo_input(device_file):
    retVal = "\x00" # return null byte by default

    if (device_file.read(2).hex() == "0104"):
        retVal = "\x0A"   # return newline character
    elif (device_file.read(2).hex() == "0108"):
        retVal = "1"
    elif (device_file.read(2).hex() == "0101"):
        retVal = "0"
    elif (device_file.read(2).hex() == "0102"):
        return "\x08"   # return backspace character

    return retVal

# input is usually sys.stdin
def keypressed(device_file):
    retVal = select.select([device_file], [], [], 0) == ([device_file], [], [])
    return retVal

# input is usually sys.stdin
def get_binary_keyboard_input(device_file):
    retVal = "\x00" # return null byte by default

    cached_terminal_settings = termios.tcgetattr(device_file.fileno())

    try:
        tty.setraw(device_file.fileno())

        typed_char = device_file.read(1).encode().hex()

        if (typed_char == "0a" or typed_char == "0d"):
            # either '\n' or '\r\n' was entered
            retVal = "\n"   # return newline character
        elif (typed_char == "31"):
            retVal = "1"
        elif (typed_char == "30"):
            retVal = "0"
        elif (typed_char == "08"):
            retVal = "\x08"   # return backspace character
        elif (typed_char == "03"):
            print ("\nExiting....") # CTRL-C, exit program
            termios.tcsetattr(device_file, termios.TCSADRAIN, cached_terminal_settings)
            exit(0)
    finally:
        termios.tcsetattr(device_file, termios.TCSADRAIN, cached_terminal_settings)

    return retVal
