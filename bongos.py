#!/usr/bin/python3

import os
from time import monotonic, strftime, sleep



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



# amount of time until bongo will register hit again
bongo_clap_length = 0.2

bongos = open("/dev/hidraw2", "rb")
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
os.system('echo "    HIT BACK RIGHT BONGO THREE TIMES TO ASSEMBLE AND RUN"')

os.system('echo "01234567 89012345 67890123 45678901"')
os.system('printf "\033[0m"')
os.system('echo "\n"')


while True:
	hid_buffer += bongos.read(2).hex()

	if (hid_buffer[-4:] == "0104" and (monotonic() - last_bongo_clap > bongo_clap_length)):
		# back right bongo hit, so insert newline in text editor
		enter_count += 1

		if (enter_count >= 3):
			# three newlines have been entered, so
			# exit while loop to write buffer to file and assemble
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

# Save the contents of text_editor_buffer to a file
save_file = open("bongo_saves/" + strftime("%Y%m%d-%H%M%S") + ".bgs", "w+")

for i in range(0, len(text_editor_buffer)):
	byte = text_editor_buffer[i]
	save_file.write("{0:b}".format(byte))
	if (i % 4 == 0 and i != 0):
		save_file.write("\n")
save_file.write(current_byte)
save_file.close()

# Clear text editor
os.system("reset")

# Confirm that each instruction is 4 bytes long
if len(text_editor_buffer) % 4 != 0 or len(current_byte) > 0:
	print("Error: Incomplete instruction in text editor, cannot assemble.")
	print("Exiting...")
	exit(0)

# Write ARM instructions to pre-assembled object file with large NOP region
os.system("as -mfpu=vfpv2 -o bongos.o bongos.s")

obj_file = open("bongos.o", "rb")
contents = obj_file.read()
before_nop_region = contents[:64] # NOP region begins at 64th byte
after_nop_region = contents[64:]
obj_file.close()

obj_file = open("bongos.o", "wb")
new_instructions = text_editor_buffer
obj_file.write(before_nop_region)
obj_file.write(new_instructions)
obj_file.write(after_nop_region[len(new_instructions):])
obj_file.close()

# Link object file and run
os.system("gcc -o bongos.out bongos.o")
os.system("./bongos.out; echo $?")
