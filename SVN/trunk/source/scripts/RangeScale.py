#!/usr/bin/python

import argparse
import sys

# ------------------------------------------------------------- #
# Python script for reading out range and scale from unit PR4000B.
# Lauren Dawson, 15.03.2016
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input', metavar='SR', type=str, nargs="+", choices = ['R1','R2','SC2','ST2', 't'],
                   help='Desired Variable Readout')

args = parser.parse_args()
inputs = args.input

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a hard-wired single number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in inputs:
  if cmd_argument == 't':
    # Return integer between 0-30 :
    print('3.000')
    sys.exit()
# If not in test mode, generate the single argument required for the rest of the script :
input = inputs[0]

import serial as s
import fcntl
import errno
import time

# Create temperorary lock file. When the script is called it will lock this file
# If the file is already locked it will wait until it is released, before locking
# and continuing execution of the script.
x = open('/var/lock/mfc_lock_file', 'w+')

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

# Get data from the PR4000B over serial interface :
# -------------------------------------------------
#ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)
# DSW, 07.09.16 : reduce the timeout, but also use read(N_BYTES) rather than readline()$
# that read commands terminate upon completion rather than upon a timeout. Therefore if$
# is working properly, we should no longer be sensitive to the "timeout" parameter.
ser = s.Serial(port='/dev/mfc', baudrate=115200, timeout=1.0, parity=s.PARITY_NONE)

# Returns range followed by the unit :
ser.write("@03?RG1\r")
ser.flush()
# Read and reformat so all on one line (the 8 bytes is empirical) :
msg = ser.read(15)
if msg == "":
        if input == 'R1' :
            print ('999')
            sys.exit()
        else :
            print ("Error reading RG1 from MFC")
            sys.exit()
else :
        range_msg = (msg.replace("\r", " ")).split(",")
# Separate message out in to range and unit :
range_ch1, unit_ch1 = range_msg

if input == "R1" :
	print (range_ch1.strip())
	sys.exit()

# Get RG2 :
ser.write("@03?RG2\r")
ser.flush()
msg = ser.read(15)
if msg == "":
        if input == 'R2' :
            print ('999')
            sys.exit()
        else :
            print ("Error reading RG2 from MFC")
            sys.exit()
else :
        range_msg = (msg.replace("\r", " ")).split(",")
range_ch2, unit_ch2 = range_msg

if input == "R2" :
	print (range_ch2.strip())
	sys.exit()

# Slave status of channel 2 :
ser.write("@03?SM2\r");
msg = ser.read(7)
if msg == "":
        print ("Error")
        sys.exit()
else :
        status = (msg.replace("\r", " ")).strip()
        # Assign status : 
        if status == '00004' :
            status = 'Slave'
        elif status == '00002':
            status = 'Independent'

if input == "ST2" :
	print (status)
	sys.exit()

# Find the scale :
ser.write("@03?SC2\r")
ser.flush()
msg = ser.read(8)
if msg == "":
        if input == 'SC2' :
            print ('999')
            sys.exit()
        else :
            print ("Error reading SC2 from MFC")
            sys.exit()
else :
        scale_ch2 = msg.replace("\r", " ")

#Convert scale in to a % if channel 2 in slave mode
if status == '00004' :
        scale_ch2 = ((float(scale_ch2)/1000)/(float(range_ch1))) * 100
        scale_ch2 = str(scale_ch2)
        scale_ch2 += " " + "%"
	
if input == "SC2" :
	print (scale_ch2.strip())
	sys.exit()
