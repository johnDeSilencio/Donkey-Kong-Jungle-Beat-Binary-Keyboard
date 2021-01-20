# DK Jungle Beat Binary Keyboard

![DK Jungle Beat Bongo Drums](https://www.lukiegames.com/assets/images/gc_dk_bongos.jpg)

A lightweight and exploratory application of the classic Gamecube DK Bongo Drums for writing binary ARM instructions on the Raspberry Pi.

Have you ever felt like assembly was too abstract a programming language? Have you ever wanted to get as close to the metal as you possibly could? Look no further! Using your DK Bongo Drums, a Gamecube adapter, and this custom application, you'll be impressing your friends with raw ARM instructions for the Raspberry Pi in no time!

### Background and Inspiration

Ever since my first "Hello World!" program, I've wanted to peel back the layers of abstraction and figure out what *really* is going on underneath the hood of a computer. It wasn't until my first computer architecture class, EENG 3117 at SLU Madrid, when I wrote out a raw instruction in all of its 32 bits of glory for the first time. Since then, the thought of bypassing the assembler and writing raw, unencoded instructions that can be executed by the CPU directly has remained with me.

But a true programmer only uses what she needs. And if we are writing raw, unencoded instructions, then all we need are ones and zeros; hence, the bongo drums.

### Required Materials

- DK Jungle Beat Bongo Drums
- Gamecube Adapter
- Raspberry Pi (tested with RPi4 so far)

### Downloading and Running

1. Clone this repository and navigate to the new directory.
2. List all of the device files currently in use on your RPi with the following command (pay special attention to the hidraw files):
```
ls /dev
```
3. Plug in your Gamecube adapter to the RPi and plug the DK Bongo Drums into the Gamecube adapter. Make sure the Gamecube adapter is in "PC" mode.
4. Run the ```ls /dev``` command again and take note of the new hidraw file. That is the HID ("Human Interface Device") file for your bongo drums
5. To enter the bongo drum text editor and start programming, run the following command, replacing ```/dev/hidraw0``` with the device file you found in #4:
```
sudo python3 bongos.py /dev/hidraw0
```

Within the text editor, the bongos give you four controls:
```
BACK LEFT BONGO   = BACKSPACE
FRONT LEFT BONGO  = 0
FRONT RIGHT BONGO = 1
BACK RIGHT BONGO  = ENTER
```
If you hit the back right bongo three times, it will exit the text editor and attempt to write your instructions to a relocatable object file that can be linked and executed. Remember that each instruction on the RPi has to be 32 bits.

---

You're on your own now. To familiarize yourself with opcode encodings for ARM assembly, I recommend assembling test code withthe GNU assembler, ```as```. If you examine the assembled object files with ```objdump```, you can see how those assembly instructions are encoded directly. Best of luck, my friends.