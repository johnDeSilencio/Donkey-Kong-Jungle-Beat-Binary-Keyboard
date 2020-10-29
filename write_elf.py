#!/usr/bin/python3

import os

os.system("as -mfpu=vfpv2 -o empty_bongos.o empty_bongos.s")
os.system("strip empty_bongos.o")
os.system("strip --remove-section=.ARM.attribues empty_bongos.o")

# Get contents of object file
obj_file = open("empty_bongos.o", "rb")
contents = obj_file.read()
obj_file.close()

elf_header = contents[:int("34", 16)]
elf_footer = contents[int("34", 16):]

new_instructions = bytearray([int("1e", 16), int("ff", 16), int("2f", 16), int("e1", 16)])
length = len(new_instructions)
half_words = int(length / 2) if length == 1 else 2


# Modify header and footer to accomodate for new instructions

elf_header = elf_header[:32] + bytearray([elf_header[32] + (length - 4 if length >= 4 else int(length/2))]) + elf_header[33:]

print(elf_footer)
elf_footer = elf_footer[:46] + elf_footer[48:]

elf_footer = elf_footer[:104] + bytearray([elf_footer[104] + length]) + elf_footer[105:]
elf_footer = elf_footer[:116] + bytearray([elf_footer[116] + (3 if length > 0 else 0)]) + elf_footer[117:]
elf_footer = elf_footer[:140] + bytearray([elf_footer[140] + length]) + elf_footer[141:]
elf_footer = elf_footer[:180] + bytearray([elf_footer[180] + length]) + elf_footer[181:]
elf_footer = elf_footer[:220] + bytearray([elf_footer[220] + length]) + elf_footer[221:]

print(elf_footer[220:228], " ", half_words)
elf_footer = elf_footer[:226] + bytearray([elf_footer[226] - half_words]) + elf_footer[227:]
elf_footer = elf_footer[:260] + bytearray([elf_footer[260] + length - (2 if length >= 4 else 0)]) + elf_footer[261:]

# Write new object file containing new instructions
new_obj_file = open("new_bongos.o", "wb")
new_obj_file.write(elf_header)
new_obj_file.write(new_instructions)
new_obj_file.write(elf_footer)
new_obj_file.close()

# Link new object file and run
os.system("ld -Ttext 34 -o new_bongos.out new_bongos.o")
os.system("./new_bongos.out")
