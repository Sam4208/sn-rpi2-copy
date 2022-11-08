#!/usr/bin/python

import serial as s
import time
import UsefulFunctions as uf

# ------------------------------------------------------------- #
# Python script for automatically changing temp.
# Lauren Dawson, 22.03.2016
# ------------------------------------------------------------- #

# Get data from the Haake over serial interface :
# -------------------------------------------------
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Activate remote control :
# -------------------------
uf.enable_remote_control()

# Adjust to 12 :
# -----------
for temp in [13,16,19,22,25] :
	ser.write("W S0 %d\r" % temp)
	ser.flush()
	msg = ser.readline()

	# Check S0 has updated:
	ser.write("S0\r")
	ser.flush()
	msg = ser.readline().replace("\r\n", '')
	set_point_0 = msg[5:].replace("$", '')

	if float(set_point_0) == float(temp) :	
		print "S0 succefully adjusted to : ", temp
	else :
		print "Error updating S0"
	
	# Print changed value to console
	print (set_point_0)

	time.sleep(7200)

