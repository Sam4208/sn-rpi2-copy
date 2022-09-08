#!/usr/bin/python

import serial as s
import argparse
import sys
import fcntl
import errno
import time

# ------------------------------------------------------------- #
# Python script for reading the temperature limits from the Haake.
# Lauren Dawson, 23.03.2016
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input', metavar='SR', type=str, nargs="+", choices = ['H','L','d','t'],
                   help='Desired Variable Readout')

args = parser.parse_args()
input = args.input

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a hard-wired single number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in input:
  if cmd_argument == 't':
    print(1.000)
    sys.exit()

import UsefulFunctionsHaake as uf

# Create temperorary lock file. When the script is called it will lock this file
# If the file is already locked it will wait until it is released, before locking
# and continuing execution of the script.
x = open('/var/lock/haake_lock_file', 'w+')

# Initialise number of attempts variable
attempts = 0

while True:
    try:
        attempts +=1
        if attempts > 45 :
          sys.exit(1)
        else :
          time.sleep(1)
          fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
          break
    except IOError as ex:
        # raise on unrelated IOErrors
        if ex.errno != errno.EAGAIN:
            raise
    else:
        time.sleep(0.1)
        
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
