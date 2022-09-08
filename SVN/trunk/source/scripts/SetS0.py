#!/usr/bin/python

import serial as s
import UsefulFunctionsHaake as uf
import time
import sys
import argparse

# ------------------------------------------------------------- #
# Python script for setting S0 on Haake.
# Lauren Dawson, 10.03.2016
# ------------------------------------------------------------- #

# Get data from the Haake over serial interface :
# -------------------------------------------------
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Get the date and time :
report_msg = uf.get_date_time()

# Command line parameters :
# -------------------------
parser = argparse.ArgumentParser(description='Adjust Set Value S0')
parser.add_argument('input1', metavar='S0', type=float,
                   help='Desired Set Value')
#parser.add_argument('input2', metavar='RO', type=str, choices = ['0','d'],
#                   help='Desired Readout Mode')
parser.add_argument('input2', metavar='RO', type=str,
                   help='Desired Readout Mode')

args = parser.parse_args()
s0 = args.input1
mode = args.input2

if mode == 'd' :
	print ("Trying to set S0 = "+ s0)

# Activate remote control :
# -------------------------
uf.enable_remote_control(mode)

# Adjust S0 :
# -----------
ser.write("W S0 %f\r" % s0)
ser.flush()
msg = ser.readline()
if msg == '':
	if mode == '0':
		print ('999')
		sys.exit()
	else :
		print ("Error updating S0")
		sys.exit()

# Check S0 has updated:
if mode == 'd' :
	ser.write("S0\r")
	ser.flush()
	msg = ser.readline().replace("\r\n", '')
	set_point_0 = msg[5:].replace("$", '')

	if float(set_point_0) == float(s0) :
		print ("S0 succefully adjusted to : "+ s0)
	else :
		print("Error updating S0")
		print (set_point_0)

	# Print changed value to console
	report_msg += set_point_0

#Disable remote control in a separate script once value has been reached
