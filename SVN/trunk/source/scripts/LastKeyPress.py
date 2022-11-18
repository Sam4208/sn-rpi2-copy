#!/usr/bin/python

import sys
import serial as s

# ----------------------------------------------------------------------- #
# Python script to retrieve the last key pressed on the PR40000B unit.
# Lauren Dawson, 19.05.2016
# Note that the unit has address "03" (default value ?)
# ----------------------------------------------------------------------- #

# Establish serial connection
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

# Write request for key press value
ser.write(b"@03KY\r")
# Clear buffer to help with lag :
ser.flush()

# Read back value and format
msg = ser.read(8).decode("UTF-8")
keypress_code = msg.strip()

if msg == "" :
	print ("Error")
	sys.exit()

# Define empty string to hold value
keypress = ""

# Asign string value to code read out
if keypress_code == "00007" :
	keypress = "OFF"
elif keypress_code == "00008" :
	keypress = "ON"
elif keypress_code == "00009" :
	keypress = "ESC"
elif keypress_code == "00010" :
	keypress = "ENTER"
elif keypress_code == "00011" :
	keypress = "RIGHT"
elif keypress_code == "00012" :
	keypress = "LEFT"
elif keypress_code == "00013" :
	keypress = "UP"
elif keypress_code == "00014" :
	keypress = "DOWN"
elif keypress_code == "00255" :
	keypress = "No Key"
else :
	keypress = "Other"
	
print (keypress)
print(keypress_code)
