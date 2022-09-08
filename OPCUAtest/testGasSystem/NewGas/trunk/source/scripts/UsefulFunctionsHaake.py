#!/usr/bin/python

# ------------------------------------------------------------- #
# Python script containing common functions used in MFC scripts
# Lauren Dawson, 10.03.2016
# ------------------------------------------------------------- #

import serial as s
import time
#import argparse
import sys

# command line parameters
#parser = argparse.ArgumentParser(description='Adjust Set Point 1')
#parser.add_argument('input2', metavar='RO', type=str,
#                   help='Desired Readout Mode')

#args = parser.parse_args()
#mode = args.input2

# Serial interface
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Start remote control of Haake
def enable_remote_control(mode):
	ser.write("GO\r")
	ser.flush()
	msg = ser.readline()
	if msg == '':
		if mode == '0':
			print 999
			sys.exit()
		else :
			print "Error starting remote control"
			sys.exit()
	else :
		print "Remote control ON"

# Stop remote control of Haake
def disable_remote_control(mode):
	ser.write("ST\r")
	ser.flush()
	msg = ser.readline()
	if msg == '' :
		if mode == '0':
			print 999
			sys.exit()
		else :
			print "Error stopping remote control"
			sys.exit()
	else :
		print "Remote control OFF"

# Function to find date and fill report msg
def get_date_time():
	date_msg = time.strftime("%d/%m/%Y")
	time_msg = time.strftime("%H:%M:%S")
	report_msg = date_msg+" "+time_msg+" : "
	return report_msg

# Function to find character in string and return its index
def find_str(s, char):
    	index = 0
	myList = []
	while index < len(s) :
        	index = s.find(char, index)
		if index == -1	:
            		break
		myList.append(index)
		index +=1
	
	return myList
