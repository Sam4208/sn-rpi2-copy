#!/usr/bin/python

import argparse
import sys

# ------------------------------------------------------------- #
# Python script for reading operating status from Haake.
# Lauren Dawson, 10.03.2016
# ------------------------------------------------------------- #

# Command line parameters :
# -------------------------
parser = argparse.ArgumentParser(description='Select Readout Mode')
parser.add_argument('input', metavar='RO', type=str, nargs="+", choices = ['0','d','t'],
                   help='Desired Readout Mode')

args = parser.parse_args()
inputs = args.input

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a random number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in inputs:
  if cmd_argument == 't':
    import random 
    tHaakeStatus = random.randrange(0,11)
    print("%.3f" % tHaakeStatus)
    sys.exit()
# If not in test mode, generate the single argument required for the rest of the script :
mode = inputs[0]

import serial as s
import UsefulFunctionsHaake as uf
import fcntl
import errno
import time

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

# Get Current Operating Status :
# ------------------------------
ser.write(b"R BS\r")
ser.flush()
msg = ser.readline()
if msg == "" :
	print ("Error communicating with device")
	sys.exit()

status_msg = str(msg[2:]).replace("$", '')

# Need to scan through response and look for 1s
# For test purposes :
# status_msg = "100000010000"
index_list = uf.find_str(status_msg, "1")

# Check for through index list and assign status:
status = ""

# Empty list if functioning normally
if not index_list :
	status = "Normal: Temp Control Off, Int Control, Main Relay Present, "
	if mode == '0':
		print (status[:-2])
		exit()
else :
	for index in index_list:
		if index == 0 :
			status += "Temp Control On, "
		elif index == 1:
			status += "Ext Control, "
		elif index == 2:
			status += "Alarm: Main Relay Missing, "
		elif index == 3:
			status += "Alarm: Overtemp, "
		elif index == 4:
			status += "Alarm: Liquid Level, "
		elif index == 5:
			status += "Alarm: Motor or Pump Overload, "
		elif index == 6:
			status += "Alarm: Via Ext Connection, "
		elif index == 7:
			status += "Alarm: Cooling, "
		elif index == 8 or 9:
			status += "Reserved Custom Alarm, "
		elif index == 10:
			status += "Alarm: Int Pt100, "
		elif index == 11:
			status += "Alarm: Ext Pt100, "
		else:
			print ("Error finding status")

if mode == '0':
	print (status[:-2])
	exit()

# Format and write the final report message :
# -------------------------------------------
report_msg += "Current Status: " +status[:-2]
report_msg += "\n"

# To screen for interactive use :
if mode == 'd':
	print (report_msg) 

	# To separate files for the log (appending) and current values :
	f_log = open('/home/supernemo/HaakeDL30Monitoring/OperatingStatus_log.txt','a')
	f_cur = open('/home/supernemo/HaakeDL30Monitoring/OperatingStatus_cur.txt','w')
	f_log.write(report_msg)
	f_cur.write(report_msg)
