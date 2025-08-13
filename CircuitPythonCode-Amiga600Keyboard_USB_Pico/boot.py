import usb_midi
import usb_cdc
import usb_hid

# Disable both serial devices
usb_cdc.disable()   
# Disable MIDI
usb_midi.disable()  
# Explictly enable keyboard and consumer control
usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.CONSUMER_CONTROL))
