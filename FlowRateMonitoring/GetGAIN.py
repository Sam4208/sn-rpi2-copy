#!/usr/bin/python

import subprocess
import serial as s
import ctypes
import sys

# ------------------------------------------------------------- #
# Get GAIN 
# ------------------------------------------------------------- #

# Establish serial connection
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

# Retrieve the GAIN :
ser.write("@03?GN1\r")
# Clear buffer to help with lag :
ser.flush()
# Read and check for errors :
msg = ser.read(8)
if msg == '' :
		print "Error"
		sys.exit()
else :
		flowmsg = msg.replace("\r\n", '')
		print flowmsg


