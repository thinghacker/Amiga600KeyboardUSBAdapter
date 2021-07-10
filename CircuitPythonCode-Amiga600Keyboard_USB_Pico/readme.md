# Amiga600 Keyboard USB Adapter CircuitPython Firmware
This project enables an existing Amiga 600 Keyboard to be USB enabled via a Raspberry Pi Pico and MCP20008.

Keyboard Maintainer:  https://github.com/thinghacker

Supported Hardware: [Amiga 600 USB Keyboard Adapter](https://github.com/thinghacker/Amiga600KeyboardUSBAdapter/tree/main/PCB-Amiga600Keyboard_USB_Pico)

### Features

- Uses CircuitPython and two Adafruit Libraries
- Uses the Amiga 600 case LEDs for Power / Number Lock (FDD) and Scroll Lock (HDD)
- For the English keyboard variant, the two blank "International" keys shift layers to support more contemporary functions such as F11, F12, Numeric Keypad and Media Keys
- [Uses a simple PCB Design](https://github.com/thinghacker/Amiga600KeyboardUSBAdapter/tree/main/PCB-Amiga600Keyboard_USB_Pico) with a small number of components

### Build Instructions
- Construct the PCB and connect it to the USB port of your computer where the Pi Pico should appear as a USB flash drive
- Download the **uf2** file from [install CircuitPython](https://circuitpython.org/board/raspberry_pi_pico/) and copy it to your Pico Pico (this code was written using version 6.3.0)
- Copy the CircuitPython HID library [Adafruit_CircuitPython_HID](https://github.com/adafruit/Adafruit_CircuitPython_HID) (adafruit_hid directory) to the **lib** directory on your Pi Pico
- Copy the CircuitPython mcp230xx library [Adafruit_CircuitPython_MCP230xx](https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx) (adafruit_mcp230xx directory) to the **lib** directory on your Pi Pico
- Copy the code.py file from this repo to your Pi Pico
- Remove the USB cable, attach the keyboard and LEDs to the Adapter
- Reattach the USB cable and type away!

Reboot and enjoy
### Keyboard Layer Configuration

#### Base Layer
![Base Layer](layout-images/A600%20Keyboard-Base.PNG)

- My particular keyboard is the UK variant (differences are shown as Green on the keys), however this keymap is configured as if it was USA.
- The Left "Blank" Key (immediately to the right of left shift) is used to enable the Additional Function Keys and Numeric Keypad Layer
- The Right "Blank" Key (above right shift) is used to enable the Media Keys Layer

#### Additional Function Keys and Numeric Keypad Layer
![Additional Function Keys and Numeric Keypad Layer](layout-images/A600%20Keyboard-Function%20and%20Keypad.PNG)

#### Media Keys Layer
![Media Keys Layer](layout-images/A600%20Keyboard-Media%20Keys.PNG)

This is broadly inspired but very much a poor mans representation of the amazing [QMK firmware](https://github.com/qmk/qmk_firmware) that is extremely limited in scope and capability but seems good enough for me.

The software as written is distributed under a GPL Version 3 License
