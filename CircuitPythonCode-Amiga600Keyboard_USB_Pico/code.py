import time
# initial delay to avoid needing to unplug/replug in some instances for keyboard detection
time.sleep(0.5)

import usb_hid
import board
import digitalio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

import board
import busio
from adafruit_mcp230xx.mcp23008 import MCP23008

i2c = busio.I2C(scl=board.GP27, sda=board.GP26)
mcp = MCP23008(i2c)  # MCP23008

# Initialize consumer control
cc = ConsumerControl(usb_hid.devices)

# Initialize Keyboard
kbd = Keyboard(usb_hid.devices)

leds = {
    "onboard": digitalio.DigitalInOut(board.LED),
    "caplock": digitalio.DigitalInOut(board.GP14),
    "fdd": digitalio.DigitalInOut(board.GP1),
    "hdd": digitalio.DigitalInOut(board.GP0),
}

for led, pinio in leds.items():
    pinio.direction = digitalio.Direction.OUTPUT

class key:
 def __init__(self, keycode, value, type):
  self.keycode = keycode
  self.value = value
  self.type = type
 def keypress(self):
  if self.type == "hidkb":
   kbd.press(self.value)
  elif self.type == "consumercontrol":
   cc.send(self.value)
 def keyrelease(self):
  if self.type == "hidkb":
   kbd.release(self.value)

class keyboard:
 def __init__(self):
  # use adafruit_hid.keycodes
  self.__keycodes = { kc: getattr(Keycode, kc) for kc in dir(Keycode) if not kc.startswith('__') and not callable(getattr(Keycode, kc)) }
  for (k,v) in self.__keycodes.items():
    setattr(self, k, key(k, v, "hidkb"))
  # use adafruit_hid.consumer_control_codes
  self.__consumercontrolcodes = {c: getattr(ConsumerControlCode, c) for c in dir(ConsumerControlCode) if not c.startswith('__') and not callable(getattr(ConsumerControlCode, c)) }
  # lots of consumer control codes are not in adafruit library but we can add https://www.usb.org/sites/default/files/hut1_21_0.pdf#page=123.
  self.__additionalconsumercontrolcodes = { "CALC": 0x192 }
  self.__consumercontrolcodes.update(self.__additionalconsumercontrolcodes)
  for (k,v) in self.__consumercontrolcodes.items():
    setattr(self, k, key(k, v, "consumercontrol"))
  self.__layershiftcodes = { "LAYERSHIFT_0": 0, "LAYERSHIFT_1": 1, "LAYERSHIFT_2": 2 }
  for (k,v) in self.__layershiftcodes.items():
    setattr(self, k, key(k, v, "layershift"))

KC = keyboard()

def initmatrix(rows, cols):
    """initmatrix

    Set the pins in array rows as output and with value high
    Set the pins in array cols as input and with pullups enabled

    returns nothing
    """
    for row in rows:
        row.direction = digitalio.Direction.OUTPUT
        row.value = True
    for column in cols:
        column.direction = digitalio.Direction.INPUT
        column.pull = digitalio.Pull.UP


def scanmatrix(rows, cols):
    """scanmatrix

    Incrementally set each row pin to low and see if a col pin is pulled low
    False indicates that a key is pressed, True key not pressed

    returns a matrix of rows and cols
    """
    matrix = []
    for row, r in enumerate(rows):
        rows[row].value = False
        for column, c in enumerate(cols):
            matrix.append(cols[column].value)
        rows[row].value = True
        time.sleep(0.01)
    return matrix


def keystatechange(matrix, oldmatrix, KEYMAP, LAYER):
    """keystatechange

    compares the current matrix (matrix) with the previous (oldmatrix) to see if there are
    any key changes or not

    If they are, consider the active keymap via Layer and determine if a key press, release
    or layer change should occur

    returns NEWLAYER
    """

    NEWLAYER = LAYER
    if matrix != oldmatrix:
      for k, v in enumerate(matrix):
        if matrix[k] != oldmatrix[k] and KEYMAP[LAYER][k] != None:
           # False if Key is pressed
           if matrix[k] is False:
               if KEYMAP[LAYER][k].type == "layershift":
                 NEWLAYER = KEYMAP[LAYER][k].value
               KEYMAP[LAYER][k].keypress()
           # True if Key is released
           elif matrix[k] is True:
               if KEYMAP[LAYER][k].type == "layershift":
                 NEWLAYER = 0
               KEYMAP[LAYER][k].keyrelease()
    return NEWLAYER

def a600keyboard():
    """a600keyboard

    Initialize system to use two keyboard matrices KEYMAP_M1 and KEYMAP_M2
    that combined represent the entire A600 keyboard

    Keyboard state changes are read and sent as USB HID messages to the host computer

    HID reports from the computer with regard to CAPS_LOCK, SCROLL_LOCK and NUM_LOCK
    for setting LED states

    The main while state loop will forever
    """

    rows1 = [
        mcp.get_pin(0),
        digitalio.DigitalInOut(board.GP16),
        mcp.get_pin(1),
        digitalio.DigitalInOut(board.GP17),
        digitalio.DigitalInOut(board.GP15),
    ]
    cols1 = [
        digitalio.DigitalInOut(board.GP19),
        digitalio.DigitalInOut(board.GP11),
        mcp.get_pin(2),
        digitalio.DigitalInOut(board.GP20),
        mcp.get_pin(6),
        digitalio.DigitalInOut(board.GP10),
        mcp.get_pin(7),
        digitalio.DigitalInOut(board.GP9),
        digitalio.DigitalInOut(board.GP21),
        digitalio.DigitalInOut(board.GP8),
        digitalio.DigitalInOut(board.GP22),
        digitalio.DigitalInOut(board.GP6),
        digitalio.DigitalInOut(board.GP7),
        digitalio.DigitalInOut(board.GP4),
        digitalio.DigitalInOut(board.GP3),
    ]
    rows2 = [digitalio.DigitalInOut(board.GP2)]
    cols2 = [
        mcp.get_pin(3),
        digitalio.DigitalInOut(board.GP13),
        mcp.get_pin(5),
        mcp.get_pin(4),
        digitalio.DigitalInOut(board.GP12),
        digitalio.DigitalInOut(board.GP18),
        digitalio.DigitalInOut(board.GP5),
    ]

    # Initialize the matrix row and col pins
    initmatrix(rows1, cols1)
    initmatrix(rows2, cols2)

    # Initialize the old matrix values
    oldmatrix1 = [True] * (len(rows1) * len(cols1))
    oldmatrix2 = [True] * (len(rows2) * len(cols2))

    # Each Keymap matrix has 3 layers (layer 0 is the normal/default)
    KEYMAP_M1 = ["LAYER0","LAYER1","LAYER2"]
    KEYMAP_M2 = ["LAYER0","LAYER1","LAYER2"]

    # Based on http://www.amigawiki.org/dnl/schematics/A600_R1.5.pdf (last page)
    # When LAYER = 0
    KEYMAP_M1[0] = [ KC.ESCAPE,          None,          KC.F1,         KC.F2,           KC.F3,          KC.F4,          KC.F5,            None,            KC.F6,           None,            KC.F7,                  KC.F8,           KC.F9,            KC.F10,              KC.F1,
                     KC.GRAVE_ACCENT,    KC.ONE,        KC.TWO,        KC.THREE,        KC.FOUR,        KC.FIVE,        KC.SIX,           KC.SEVEN,        KC.EIGHT,        KC.NINE,         KC.ZERO,                KC.MINUS,        KC.EQUALS,        KC.BACKSLASH,        KC.UP_ARROW,
                     KC.TAB,             KC.Q,          KC.W,          KC.E,            KC.R,           KC.T,           KC.Y,             KC.U,            KC.I,            KC.O,            KC.P,                   KC.LEFT_BRACKET, KC.RIGHT_BRACKET, KC.RETURN,           KC.LEFT_ARROW,
                     KC.CAPS_LOCK,       KC.A,          KC.S,          KC.D,            KC.F,           KC.G,           KC.H,             KC.J,            KC.K,            KC.L,            KC.SEMICOLON ,          KC.QUOTE,        KC.LAYERSHIFT_1,  KC.DELETE,           KC.RIGHT_ARROW,
                     KC.LAYERSHIFT_2,    KC.Z,          KC.X,          KC.C,            KC.V,           KC.B,           KC.N,             KC.M,            KC.COMMA,        KC.PERIOD,       KC.FORWARD_SLASH,       None,            KC.SPACE,         KC.BACKSPACE,        KC.DOWN_ARROW ]
    KEYMAP_M2[0] = [ KC.RIGHT_SHIFT,     KC.RIGHT_ALT,  KC.RIGHT_GUI,  KC.CONTROL,      KC.LEFT_SHIFT,  KC.LEFT_ALT,    KC.LEFT_GUI]

    # When LAYER = 1
    KEYMAP_M1[1] = [ None,               None,          KC.F11,        KC.F12,          None,           None,           None,             None,            None,            None,            None,                   None,            None,             None,                KC.MUTE,
                     KC.KEYPAD_ASTERISK, KC.KEYPAD_ONE, KC.KEYPAD_TWO, KC.KEYPAD_THREE, KC.KEYPAD_FOUR, KC.KEYPAD_FIVE, KC.KEYPAD_SIX,    KC.KEYPAD_SEVEN, KC.KEYPAD_EIGHT, KC.KEYPAD_NINE,  KC.KEYPAD_ZERO,         KC.KEYPAD_MINUS, KC.KEYPAD_PLUS,   KC.KEYPAD_BACKSLASH, KC.PAGE_UP,
                     None,               None,          None,          None,            None,           None,           None,             None,            None,            None,            KC.PRINT_SCREEN,        None,            None,             KC.KEYPAD_ENTER,     KC.HOME,
                     None,               None,          KC.SCROLL_LOCK,None,            None,           None,           KC.PAUSE,         None,            None,            None,            None,                   None,            KC.LAYERSHIFT_0,     None,                KC.END,
                     None,               None,          None,          None,            None,           None,           KC.KEYPAD_NUMLOCK,None,            None,            KC.KEYPAD_PERIOD,KC.KEYPAD_FORWARD_SLASH,None,            None,             None,                KC.PAGE_DOWN ]
    KEYMAP_M2[1] = [ None,               None,          None,          None,            None,           None,           None       ]

    # When LAYER = 2
    KEYMAP_M1[2] = [ None,               None,          None,          None,            None,           None,           None,             None,            None,            None,            None,                   None,            None,             None,                KC.MUTE,
                     None,               None,          None,          None,            None,           None,           None,             None,            None,            None,            None,                   None,            None,             None,                KC.VOLUME_INCREMENT,
                     None,               None,          None,          None,            None,           None,           None,             None,            None,            None,            None,                   None,            None,             KC.STOP,             KC.SCAN_PREVIOUS_TRACK,
                     None,               None,          None,          None,            None,           None,           None,             None,            None,            None,            None,                   None,            None,             None,                KC.SCAN_NEXT_TRACK,
                     KC.LAYERSHIFT_0,    None,          None,          KC.CALC,         None,           None,           None,             None,            None,            None,            None,                   None,            KC.PLAY_PAUSE,    None,                KC.VOLUME_DECREMENT ]
    KEYMAP_M2[2] = [ None,               None,          None,          None,            None,           None,           None       ]

    LAYER = 0

    kbd.release_all()

    # Main Keyboard Loop
    while 1:
        matrix1 = scanmatrix(rows1, cols1)
        LAYER = keystatechange(matrix1, oldmatrix1, KEYMAP_M1, LAYER)

        matrix2 = scanmatrix(rows2, cols2)
        LAYER = keystatechange(matrix2, oldmatrix2, KEYMAP_M2, LAYER)

        oldmatrix1 = matrix1
        oldmatrix2 = matrix2

        leds["caplock"].value = kbd.led_on(Keyboard.LED_CAPS_LOCK)
        leds["fdd"].value = kbd.led_on(Keyboard.LED_NUM_LOCK)
        leds["hdd"].value = kbd.led_on(Keyboard.LED_SCROLL_LOCK)


if __name__ == "__main__":
    a600keyboard()
