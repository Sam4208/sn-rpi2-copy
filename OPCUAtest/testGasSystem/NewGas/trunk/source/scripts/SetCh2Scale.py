#!/usr/bin/python

import serial as s
import ctypes
import argparse
import UsefulFunctions as uf
import sys

txt = """The value of SCL (Scaler) determines the ratio of the setpoint which will be applied to the slave. 
Example for two mass flow controllers:
Channel 1: MFC 500 sccm full scale, Mode Independent. (This is the master channel!)
Channel 2: MFC 200 sccm full scale, Mode Slave. (Scaler SCL set to 080.00 sccm)

When the master's flow readout ranges from 0-500 sccm the setpoint applied to the slave ranges proportionally from 0-80 sccm ! The gas mixing ratio therefore is set to: 500 : 80 = 6,25 : 1"""

parser = argparse.ArgumentParser(description=txt)
parser.add_argument('scale', metavar='Scale', type=float,
                   help='Desired scale')
parser.add_argument('input', metavar='RO', type=str, choices = ['0','d'],
                   help='Desired Readout Mode')

args = parser.parse_args()
scale = args.scale
input = args.input

if input == 'd' :
	print "Trying to set scale = ", scale

# Get data from the PR4000B over serial interface :
# -------------------------------------------------
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

# BEGIN remote control ####

#enable remote control
uf.enable_remote_control(input)

# change ch2 mode to slave (mode=4)
if input == 'd' :
	print 'Change ch2 mode to slave '

ser.write("@03?SM2,4\r");
ser.flush()
if input == 'd' :
	print 'Response : ', ser.readline()

# set scale (aka scale)
if input == 'd' :
	print 'Adjusting ch2 scale to %0.2f' % scale

ser.write("@03?SC2,%0.2f\r" % scale);
ser.flush()
msg = ser.readline()
if msg == '' :
	if input == '0' :
		print 999
		sys.exit()
	else :
		print "Error writing scale"
		sys.exit()
print 'Response : ', msg
if input == '0' :
	uf.disable_remote_control(input)
	sys.exit()

# Read SC2 value back and check updated
if input == 'd' :
	ser.write("@03?SC2\r")
	ser.flush()
	msg = ser.readline()
	if msg == "":
        	print "Error reading SC2 from MFC"
        	sys.exit()
	else :
       		scale_ch2 = msg.replace("\r", " ")

	if float(scale) == float(scale_ch2) :
		print "Successfully changed SC2"
	else :
		print "Error changing SC2"

	#disable remote control
	uf.disable_remote_control(input)
#### END ####
