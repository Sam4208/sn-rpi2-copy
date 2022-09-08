#!/usr/bin/python

import serial as s
import UsefulFunctionsHaake as uf
import argparse
import sys

# ------------------------------------------------------------- #
# Python script for reading operating status from Haake.
# Lauren Dawson, 10.03.2016
# ------------------------------------------------------------- #

# Get data from the Haake over serial interface :
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)

# Command line parameters :
# -------------------------
parser = argparse.ArgumentParser(description='Select Readout Mode')
parser.add_argument('input', metavar='RO', type=str, choices = ['0','d'],
                   help='Desired Readout Mode')

args = parser.parse_args()
mode = args.input

# Get the date and time :
report_msg = uf.get_date_time()

# Get Current Operating Status :
# ------------------------------
ser.write("R BS\r")
ser.flush()
msg = ser.readline()
if msg == "" :
	print "Error"
	sys.exit()

status_msg = msg[2:].replace("$", '')

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
		print status[:-2]
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
			print "Error finding status"

if mode == '0':
	print status[:-2]
	exit()

# Format and write the final report message :
# -------------------------------------------
report_msg += "Current Status: " +status[:-2]
report_msg += "\n"

# To screen for interactive use :
if mode == 'd':
	print report_msg 

	# To separate files for the log (appending) and current values :
	f_log = open('/home/supernemo/HaakeDL30Monitoring/OperatingStatus_log.txt','a')
	f_cur = open('/home/supernemo/HaakeDL30Monitoring/OperatingStatus_cur.txt','w')
	f_log.write(report_msg)
	f_cur.write(report_msg)
