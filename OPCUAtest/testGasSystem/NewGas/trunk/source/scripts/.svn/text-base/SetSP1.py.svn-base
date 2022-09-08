#!/usr/bin/python

import serial as s
import ctypes
import time
import argparse
import UsefulFunctions as uf
import sys

# ------------------------------------------------------------- #
# Python script for talking to MKS controller unit PR4000B.
# Dave Waters, 28.08.2015
# M. Cascella, 11.11.2015
# Note that the unit has address "03" (default value ?)
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Adjust Set Point 1')
parser.add_argument('input1', metavar='SP', type=float,
                   help='Desired Set Point')
parser.add_argument('input2', metavar='RO', type=str, choices = ['0','d'],
                   help='Desired Readout Mode')

args = parser.parse_args()
sp1 = args.input1
mode = args.input2

if mode == 'd' :
	if sp1 > 22 :
		print "Cannot set SP1 above 22, setting to 22 (max) by default"

	print "Trying to set SP1 = ", sp1

# Get data from the PR4000B over serial interface :
# -------------------------------------------------
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

#### BEGIN active part ####

#enable remote control
uf.enable_remote_control(mode)

# adjust SP1
if mode == 'd' :
	print 'Adjusting set point to %0.2f' % sp1
ser.write("@03?SP1,%0.2f\r" % sp1);
msg = ser.readline()
if msg == '':
	if mode == '0' :
		print 999
		sys.exit()
	else :
		print "Error writing set point"
		sys.exit()
else:
	if mode == '0' :
		print msg.strip()
	else :
		print 'Response : ', msg

#disable remote control
uf.disable_remote_control(mode)

# Get the date and time :
# -----------------------
if mode == 'd' :
	report_msg = uf.get_date_time()

# Get the set points and actual values :
if mode == 'd' :
	ser.write("@03?SP1\r")
	ser.flush()
	set_point_ch1 = ser.readline()
	set_point_ch1 = set_point_ch1.replace("\r", " ")
	ser.write("@03?SP2\r")
	ser.flush()
	set_point_ch2 = ser.readline()
	set_point_ch2 = set_point_ch2.replace("\r", " ")
	ser.write("@03?AV1\r")
	ser.flush()
	flow_ch1 = ser.readline()
	flow_ch1 = flow_ch1.replace("\r", " ")
	ser.write("@03?AV2\r")
	ser.flush()
	flow_ch2 = ser.readline()
	flow_ch2 = flow_ch2.replace("\r", " ")

	if float(set_point_ch1) == float(sp1) :
		print "SP1 successfully changed"
	else :
		print "Error: SP1 not updated, check that value entered is not greater than max (22)"

# Format and write the final report message :
# -------------------------------------------
if mode == 'd' :
	report_msg += "SP1:"  +set_point_ch1 
	report_msg += " SP2:" +set_point_ch2
	report_msg += "FR1:"  +flow_ch1      
	report_msg += " FR2:" +flow_ch2
	report_msg += "\r\n"

# To screen for interactive use :
	print report_msg

