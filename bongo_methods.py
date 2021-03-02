import os
import sys
from time import monotonic, strftime, sleep
import socket
import binascii
import uuid
import re
import argparse

def get_binary_bongo_input(device_file):
    if (device_file.read(2).hex() == "0104"):
        return "\x0A"   # return newline character
    elif (device_file.read(2).hex() == "0108"):
        return "1"
    elif (device_file.read(2).hex() == "0101"):
        return "0"
    elif (device_file.read(2).hex() == "0102"):
        return "\x08"   # return backspace character
    else:
        return "\x00"   # return null byte otherwise
