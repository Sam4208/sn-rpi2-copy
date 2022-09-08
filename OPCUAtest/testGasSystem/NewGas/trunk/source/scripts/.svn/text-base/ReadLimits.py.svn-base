#!/usr/bin/python

import serial as s
import UsefulFunctionsHaake as uf
import argparse
import sys

# ------------------------------------------------------------- #
# Python script for reading the temperature limits from the Haake.
# Lauren Dawson, 23.03.2016
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input', metavar='SR', type=str, choices = ['H','L','d'],
                   help='Desired Variable Readout')

args = parser.parse_args()
input = args.input

# Get data from the Haake over serial interface :
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Get the date and time :
report_msg = uf.get_date_time()

# Read high limit on temperature :
ser.write("HL\r")
ser.flush()
msg = ser.readline().replace("\r\n", '')
if msg == "" :
	if input == 'H' :
		print 999
		sys.exit()
	elif input == 'd' :
		print "Error reading high limit"
		sys.exit()
high_limit = msg[5:].replace("$", '')
if input == 'H' :
	print high_limit
	sys.exit()

# Read low limit on temperature :
ser.write("LL\r")
ser.flush()
msg = ser.readline().replace("\r\n", '')
if msg == "" :
	if input == 'L' :
		print 999
		sys.exit()
	elif input == 'd' :
		print "Error reading low limit"
		sys.exit()
low_limit = msg[5:].replace("$", '')
if input == 'L' :
	print low_limit
	sys.exit()

# Format and write the final report message :
# -------------------------------------------
report_msg += "High Limit: " +high_limit + " "
report_msg += "Low Limit: " +low_limit 
report_msg += "\r\n"

if input == 'd' :
	print report_msg
