#!/usr/bin/python

# ------------------------------------------------------------- #
# Python script to read in 1 value from the pressure logger
# Lauren Dawson, 08.05.2017
# ------------------------------------------------------------- #

import time
import os
import argparse
import sys

# Command line parameters:
#-------------------------
parser = argparse.ArgumentParser(description='Chose Readout Mode')
parser.add_argument('input', metavar='RO', type=str, nargs="+", choices = ['0', 'd', 't'], help='Desired Readout')

args = parser.parse_args()
inputs = args.input

# Set up output for test mode:
#-----------------------------
for cmd_argument in inputs:
	if cmd_argument == 't':
		import random
		tpressure = random.gauss(100000,100)
		print("%i" % tpressure)
		sys.exit()

import fcntl
# Create temperorary lock file. When the script is called it will lock this file
# If the file is already locked it will wait until it is released, before locking
# and continuing execution of the script.
x = open('/var/lock/pressure_amb_lock_file', 'w+')

# Initialise counting variable
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

mode = inputs[0]
# Get the date and time :
# -----------------------
date_msg = time.strftime("%d/%m/%Y")
time_msg = time.strftime("%H:%M:%S")
report_msg = date_msg+" "+time_msg+" :"

# Run tool for retrieving raw data from the logger:
#-------------------------------------------------
output = os.popen('sudo /home/supernemo/pypressure.sh').read()

# Format data to show only pressure reading:
# -----------------------------------------
s = str(output)
t = s.rstrip()
u = s.split(',')[2]

final_msg = report_msg + u
if mode == 'd':
	print (final_msg)
elif mode == '0':
	msg = u.strip()
	print (msg)
