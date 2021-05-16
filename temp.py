import sys
import select
import tty
import termios

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setcbreak(sys.stdin.fileno())

    i = 0
    while 1:
        print(i)
        i += 1

        if isData():
            c = sys.stdin.read(1)
            if c == '\x1b':         # x1b is ESC
                break

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

