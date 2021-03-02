import os
import sys
from time import monotonic, strftime, sleep
import socket
import binascii
import uuid
import re
import argparse

"""
	Given an array of bytes and a string
	representation of the current byte,
	will clear the current line and reprint it
"""
def reprint(byte_array, current_byte):
	# put cursor up one line
	os.system('printf "\\033[1A"')
	# delete current printed line
	os.system('printf "\\033[K"')


	# reprint current line without deleted bit
	current_line_bytes = len(byte_array) % 4

	if len(byte_array) > 0 and len(byte_array) % 4 == 0 and len(current_byte) == 0:
		# special case: line has full instruction, 32 bits
		current_line_bytes = 4

	for i in range(len(byte_array) - current_line_bytes, len(byte_array)):
		byte = "{0:b}".format(byte_array[i])
		byte = (8 - len(byte)) * "0" + byte # pad with zeros if byte < 128
		print(byte + " ", end='')
	print(current_byte)


def GetSMAC(packet):
	return binascii.hexlify(packet[6:12]).decode()

def GetDMAC(packet):
	return binascii.hexlify(packet[0:6]).decode()

def GetEtherType(packet):
	return binascii.hexlify(packet[12:14]).decode()

def GetIP(packet):
	return binascii.hexlify(packet[14:34]).decode()

def GetUDP(packet):
	return binascii.hexlify(packet[34:42]).decode()

def GetPayload(packet):
	return binascii.hexlify(packet[42:]).decode()


def ip_checksum(packet_bytearray):
    bytes_left = len(packet_bytearray)
    sum = 0

    # add header bytes to sum two bytes at a time
    while (bytes_left > 1):
        lower_short_boundary = len(packet_bytearray) - bytes_left
        upper_short_boundary = len(packet_bytearray) - bytes_left + 2
        sum += int(packet_bytearray[lower_short_boundary:upper_short_boundary].hex(), 16)
        bytes_left -= 2    # process two bytes at a time

    # if there is one byte left, make sure to add it too
    if (bytes_left == 1):
        sum += int(packet_bytearray[-1:].hex(), 16)

    # add back carry outs from the top 16 bits to the bottom 16 bits
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    sum = ~sum
    return bytearray([(sum & 0xff00) >> 8, sum & 0xff])


def display_network_header_info():
    os.system('printf "\033[0;33m"')
    os.system('echo "[*] DK BONGO DRUM BINARY TEXT EDITOR [*]"')
    os.system('echo "    LEFT  BONGO = 0"')
    os.system('echo "    RIGHT BONGO = 1"')
    os.system('echo "    HIT BACK LEFT BONGO TO BACKSPACE"')
    os.system('echo "    HIT BACK RIGHT BONGO THREE TIMES TO SEND PACKET\n"')

    os.system('echo "\t\tETHERNET HEADER"')
    os.system('echo "\t\t\t48 bits -> Destination MAC Address"')
    os.system('echo "\t\t\t48 bits -> Source MAC Address"')
    os.system('echo "\t\t\t8  bits -> Type (usually 0x08000 for IPv4)\n"')
    os.system('echo "\t\tIPv4 HEADER"')
    os.system('echo "\t\t\t4  bits -> Version (usually 0x4)"')
    os.system('echo "\t\t\t4  bits -> Header length (usually 0x5)"')
    os.system('echo "\t\t\t8  bits -> Type of service (usually 0x00)"')
    os.system('echo "\t\t\t16 bits -> Total length (in bytes)"')
    os.system('echo "\t\t\t16 bits -> Idenitifcation # (must be unique between packets)"')
    os.system('echo "\t\t\t16 bits -> Flags (Reserved bit (0), Don\'t Fragment, More Fragments, and Fragment Offset #)"')
    os.system('echo "\t\t\t8  bits -> TTL (time to live)"')
    os.system('echo "\t\t\t8  bits -> Protocol (TCP is 0x0006, UDP is 0x0011)"')
    os.system('echo "\t\t\t16 bits -> Header checksum"')
    os.system('echo "\t\t\t32 bits -> Source IPv4 address"')
    os.system('echo "\t\t\t32 bits -> Destination IPv4 address\n"')
    os.system('echo "\t\tUDP HEADER"')
    os.system('echo "\t\t\t16 bits -> Source port"')
    os.system('echo "\t\t\t16 bits -> Destination port"')
    os.system('echo "\t\t\t16 bits -> Length"')
    os.system('echo "\t\t\t16 bits -> Checksum\n"')

    os.system('echo "01234567 01234567 01234567 01234567"')
    os.system('printf "\033[0m"')
    os.system('echo "\n"')