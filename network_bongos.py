#!/usr/bin/python3

import os
import sys
from time import monotonic, strftime, sleep
import socket
import binascii
import uuid
import re
import argparse

# Initialize CLI argument parser
description = """
A binary text editor that uses the DK Bongos from \"Donkey Kong
Jungle Beat\" as a binary keyboard, either for writing raw, executable
ARM instructions or raw UDP packets with Ethernet, IP, and UDP headers.

To use the bongo drums, provide their device file as a command-line
argument. Running the program without a command-line argument will
use the default keyboard '0', '1', 'backspace', and 'enter' keys instead."""
parser = argparse.ArgumentParser(description=description)
mode = parser.add_mutually_exclusive_group()

parser.add_argument('-d', '--devfile', help='device file of bongo drums, e.g. /dev/hidraw0')
parser.add_argument('-f', '--filename', help='binary file to load into editor')
mode.add_argument('-x', '--executable', help='Instruction editor mode. Interpret and execute binary as 32-bit ARM instructions', action='store_true')
mode.add_argument('-n', '--network', help='Packet editor mode. Interpret and send binary as UDP packet', action='store_true')
parser.add_argument('-s', '--save', help='save binary to the given file')

# Parse arguments and validate command-line inputs

args = parser.parse_args()

bongo_dev_file = ""
LOAD_FILE = ""
SAVE_FILE = ""

if (args.devfile == None):
	print("No bongo drums! Using default keyboard...")
elif (re.search("/dev/.*", args.devfile) == None or not os.path.exists(args.devfile)):
	print("Error: Invalid device file for DK Bongo Drums.")
	print("Device file should be of the form \"/dev/hidrawX\".")
	print("Exiting...")
	exit(1)
else:
	bongo_dev_file = args.devfile
	print("Using bongos drums located at {0}...".format(bongo_dev_file))

if (args.filename == None):
	print("Creating an empty text editor...")
elif (args.filename != None and not os.path.exists(args.filename)):
	print("Error: binary file \"{0}\" does not exist.".format(args.filename))
	print("Exiting...")
	exit(1)
else:
	print("Loading \"{0}\" into the text editor...".format(args.filename))
	LOAD_FILE = args.filename

exit(0)


if (len(sys.argv) == 2 and re.search("/dev/.*", sys.argv[1]) == None):
    
    parser.parse_args()
    exit(1)




if (len(sys.argv) > 2 and os.path.exists(sys.argv[2])):
	SAVE_FILE = sys.argv[2]

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


# amount of time until bongo will register hit again
bongo_clap_length = 0.2

bongos = open(bongo_dev_file, "rb")
hid_buffer = ""
last_bongo_clap = monotonic()

text_editor_buffer = bytearray()
current_byte = ""
enter_count = 0

# clear screen for text editor
os.system("clear")

# display text editor banner
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

if (SAVE_FILE != ""):
	with open(SAVE_FILE, "rb") as save_file:
		# Read in file byte by byte and store in bytearray buffer
		text_editor_buffer = bytearray()
		for byte in save_file.read():
			text_editor_buffer.append(byte)
		# Print the bytes to the text editor screen
		for line in range(0, int(len(text_editor_buffer) / 4)):
			reprint(text_editor_buffer[4*line:4*line+4], current_byte)
			print("")
		reprint(text_editor_buffer[-(len(text_editor_buffer)%4):], current_byte)

while True:
	hid_buffer += bongos.read(2).hex()

	if (hid_buffer[-4:] == "0104" and (monotonic() - last_bongo_clap > bongo_clap_length)):
		# back right bongo hit, so insert newline in text editor
		enter_count += 1

		if (enter_count >= 3):
			# three newlines have been entered, so
			# exit while loop to write buffer to send packet if possible
			break

		hid_buffer = ""

		last_bongo_clap = monotonic()
	elif (hid_buffer[-4:] == "0108" and (monotonic() - last_bongo_clap > bongo_clap_length)):
		# front right bongo hit, so insert 1 in text editor

		current_byte += "1"

		if len(current_byte) == 8:
			# write new byte to text_editor_buffer
			text_editor_buffer.append(int(current_byte, 2))
			current_byte = ""

		reprint(text_editor_buffer, current_byte)
		if (8*len(text_editor_buffer)+len(current_byte)) % 32 == 0:
			print()

		hid_buffer = ""
		last_bongo_clap = monotonic()
		enter_count = 0
	elif (hid_buffer[-4:] == "0101" and (monotonic() - last_bongo_clap > bongo_clap_length)):
		# front left bongo hit, so insert 0 in text editor

		current_byte += "0"

		if len(current_byte) == 8:
			# write new byte to text_editor_buffer
			text_editor_buffer.append(int(current_byte, 2))
			current_byte = ""

		reprint(text_editor_buffer, current_byte)
		if (8*len(text_editor_buffer)+len(current_byte)) % 32 == 0:
			print()

		hid_buffer = ""
		last_bongo_clap = monotonic()
		enter_count = 0
	elif (hid_buffer[-4:] == "0102" and (monotonic() - last_bongo_clap > bongo_clap_length)):
		# back left bongo hit, so remove last character in text editor

		if len(current_byte) == 0:
			# even number of bytes have been written,
			# so we have to delete a bit from the last byte entered
			last_byte = "{0:b}".format(text_editor_buffer.pop())
			last_byte = (8 - len(last_byte)) * "0" + last_byte # pad with zeros if last_byte < 128
			current_byte = last_byte[:-1]
		else:
			current_byte = current_byte[:-1]

		if len(text_editor_buffer) % 4 == 0 and len(current_byte) == 0 and len(text_editor_buffer) > 0:
			# no bits should be on current line, so delete and go up to next line
			os.system('printf "\\033[1A"')
			os.system('printf "\\033[K"')

		reprint(text_editor_buffer, current_byte)
		hid_buffer = ""
		last_bongo_clap = monotonic()
		enter_count = 0

bongos.close()

# Save written packet to a CAP file for later use
save_file = open("network_bongo_saves/" + strftime("%Y_%m_%d_%H%M%S") + ".cap", "wb")

for byte in text_editor_buffer:
	save_file.write(bytearray([byte]))

save_file.close()

# Initialize raw socket that will allow us to send and receive network packets
host = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
s.bind(("wlan0", 3))

if (len(text_editor_buffer) < 42):
	print("Error: Packet must contain a valid ethernet and")
	print("IPv4 header to be processed. Too few bytes written.")
	print("Exiting...")
	s.close()
	exit(1)

packet = text_editor_buffer

ethernet_header = packet[:14]
ip_header = packet[14:34]
udp_header = packet[34:42]
datagram = packet[42:]

# Calculate lengths for header
ip_length = len(ip_header) + len(udp_header) + len(datagram)
ip_length = bytearray([ip_length >> 8, ip_length & 0xff])
ip_header[2:4] = ip_length

udp_length = len(udp_header) + len(datagram)
udp_length = bytearray([udp_length >> 8, udp_length & 0xff])
udp_header[4:6] = udp_length

# Construct pseudo header for UDP checksum calculation
source = ip_header[12:16]
destination = ip_header[16:20]
protocol = ip_header[9:10]
pseudo_header = source + destination + bytearray([0]) + protocol + udp_length

# Calculate checksums for headers
ip_header[10:12] = ip_checksum(ip_header)
udp_header[6:8] = ip_checksum(pseudo_header + udp_header + datagram)

packet = ethernet_header + ip_header + udp_header + datagram

print("SENT PACKET:\n")
print("Destination MAC:\t",GetDMAC(packet))
print("Source MAC:\t\t",GetSMAC(packet))
print("IP Version:\t\t",GetEtherType(packet))
print("IP Header:\t\t",GetIP(packet))
print("UDP Header:\t\t",GetUDP(packet))
print("Payload:\n")
print(GetPayload(packet),"\n")

mac_address = uuid.getnode()
mac_address = "000" + hex(mac_address)[2:]

s.send(packet)
packet = s.recvfrom(65565)
packet = packet[0]

while (GetDMAC(packet) != mac_address or GetUDP(packet)[:4] != "007b"):
	packet = s.recvfrom(65565)
	packet = packet[0]

print("RECEIVED PACKET:\n")
print("Destination MAC:\t", GetDMAC(packet))
print("Source MAC:\t\t",GetSMAC(packet))
print("IP Version:\t\t",GetEtherType(packet))
print("IP Header:\t\t",GetIP(packet))
print("UDP Header:\t\t",GetUDP(packet))
print("Payload:\n\n",GetPayload(packet))
s.close()

