#!/usr/bin/python

import serial as s
import UsefulFunctionsHaake as uf
import argparse
import sys

# ------------------------------------------------------------- #
# Python script for resetting Haake DL30 unit.
# Lauren Dawson, 31.03.2016
# ------------------------------------------------------------- #
# command line parameters
parser = argparse.ArgumentParser(description='Adjust Set Point 1')
parser.add_argument('input2', metavar='RO', type=str, choices = ['0','d'],
                   help='Desired Readout Mode')

args = parser.parse_args()
mode = args.input2

# Get data from the Haake over serial interface :
# -----------------------------------------------
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Activate remote control :
# -------------------------
uf.enable_remote_control(mode)

# Reset Unit
ser.write("RS\r")
ser.flush()
msg = ser.readline()

if msg == '' :
	if mode == "d" :
		print "Error resetting unit"
		sys.exit()
	elif mode == "0" :
		print 999
		sys.exit()

if mode == 'd' :
	print "Resetting Haake Unit"
else :
	print 'Response : ', msg

# Deactivate remote control :
# ---------------------------
uf.disable_remote_control(mode)
