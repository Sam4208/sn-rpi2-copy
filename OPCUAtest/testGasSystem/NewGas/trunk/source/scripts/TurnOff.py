#!/usr/bin/python

import serial as s
import ctypes
import UsefulFunctions as uf
import argparse
import sys
 
# ------------------------------------------------------------- #
# Python script for talking to MKS controller unit PR4000B.
# Dave Waters, 28.08.2015
# M. Cascella 11/11/15
# Note that the unit has address "03" (default value ?)
# ------------------------------------------------------------- #
# command line parameters
parser = argparse.ArgumentParser(description='Adjust Set Point 1')
parser.add_argument('input2', metavar='RO', type=str, choices = ['0','d'],
                   help='Desired Readout Mode')

args = parser.parse_args()
mode = args.input2

# Establish serial connection
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

#### BEGIN active part ####

#enable remote control
uf.enable_remote_control(mode)

# turn off both channels 
if mode == 'd' :
	print 'Turning off both channels'
ser.write("@03?VL0,OFF\r");
ser.flush()
msg = ser.readline()
if msg == '' :
		if mode == '0' :
			print 999
			sys.exit()
		else :
			print "Error turning off channels"
			sys.exit()
else :
	if mode == '0' :
		print 1
	else : 
		print 'Response : ', msg

#disable remote control
uf.disable_remote_control(mode)
