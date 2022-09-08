#!/usr/bin/python

import argparse
import sys

# Command line parameters :
# -------------------------
parser = argparse.ArgumentParser(description='Chose Readout Mode')
parser.add_argument('input', metavar='RO', type=str, choices = ['0', 'd', 't'],
                   help='Desired Readout')
args = parser.parse_args()
mode = args.input

# this goes right after reading the command line parameters,
# if we are in test mode we do not need to do much else
if mode == 't':
	#Produce random integer as the pressure variable for test mode
    import random
    tpressure = random.gauss(1,.1)
    print("%.3f" % tpressure)
    sys.exit()

import serial as s
import ctypes
import time
from time import sleep
import UsefulFunctionsPressure as uf

#establish serial connection
ser = s.Serial(port='/dev/pressure', bytesize=s.SEVENBITS,
	baudrate=2400, timeout=1, parity=s.PARITY_NONE,
	stopbits=s.STOPBITS_ONE)

#get displayed value
ser.write("!0000/");
ser.flush()

# Get the date and time :
# -----------------------
report_msg = uf.get_date_time()

#read result, number of bits to read specified
msg = ser.readline(9)

#exit if message returns blank
if(msg=='') : 
	if mode == '0' :
		print 999
		sys.exit()
	else :
		print "Error in pressure reading, EV94 replied: ", msg
		sys.exit()

#get only the relevant part of the reply
disp_str = msg[4:8]
#convert the string to hex
disp_hex = int(disp_str,16)
#read the hex as a signed short
pressure = ctypes.c_short(disp_hex).value
#convert pressure to a float
pressure = float(pressure)

#calling readline twice too fast fails randomly
sleep(.01)

#get decimal point position
ser.write("!0005/");
ser.flush()
#read result
msg = ser.readline(9)

#exit if message returns blank
if(msg=='') : 
	if mode == '0' :
		print 999
		sys.exit()
	else :
		print "Error during decimal point reading, EV94 replied: ", msg
		sys.exit()

#get only the relevant part of the reply
pos_str = msg[4:8]
#convert the string to int
pos_hex = int(pos_str)

#add decimal place to pressure value
pressure = pressure/(10**pos_hex)
pressureString = str(pressure)

if mode == 'd':
	report_msg += "Current Pressure: " + pressureString
	print report_msg
else :
	print pressure 



