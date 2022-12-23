#!/usr/bin/python

import argparse
import sys

# ------------------------------------------------------------- #
# Python script for reading set point values from Haake.
# Lauren Dawson, 10.03.2016
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input', metavar='SR', type=str, nargs="+", choices = ['T','S0','d','t'],
                   help='Desired Variable Readout')

args = parser.parse_args()
inputs = args.input

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a random number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in inputs:
  if cmd_argument == 't':
    import random 
    tHaake = random.randrange(0,14)
    print("%.3f" % tHaake)
    sys.exit()
# If not in test mode, generate the single argument required for the rest of the script :
input = inputs[0]

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

# Get Active Set Values :
# -----------------------
ser.write(b"S0\r")
ser.flush()

# Reformat response for reporting :
msg = str(ser.readline()).replace("\\r\\n'", '')
set_point_0 = msg[5:].replace("$", '')
if input == "S0" :
	# Need to check if message is blank, if so return '999', out of range value
	if set_point_0 == "" :
		print ('999')
		sys.exit()
	else :
		print (set_point_0.strip())
		sys.exit()

# Get Current Sensor Reading :
# ----------------------------
ser.write(b"I\r")
ser.flush()
msg = str(ser.readline()).replace("\\r\\n'", '')
internal_sensor = msg[5:].replace("$", '')
if input == "T" :
#        internal_sensor = ""
	if internal_sensor == "" :
		print ('999')
		sys.exit()
	else :
		print (internal_sensor.strip())
         #       print('999')

		sys.exit()


if input == 'd' :
	ser.write(b"S1\r")
	ser.flush()	
	msg = str(ser.readline()).replace("\\r\\n'", '')
	set_point_1 = msg[5:].replace("$", '')

	ser.write(b"S2\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')
	set_point_2 = msg[5:].replace("$", '')

	ser.write(b"S3\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')
	set_point_3 = msg[5:].replace("$", '')

	# Get RTA Correction Factors :
	# ----------------------------
	ser.write(b"IS\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')        
	correction_factor_0 = msg[3:].replace("$", '')

	ser.write(b"I1\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')
	correction_factor_1 = msg[3:].replace("$", '')

	ser.write(b"I2\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')
	correction_factor_2 = msg[3:].replace("$", '')

	ser.write(b"I3\r")
	ser.flush()
	msg = str(ser.readline()).replace("\\r\\n'", '')
	correction_factor_3 = msg[3:].replace("$", '')


# Format and write the final report message :
# -------------------------------------------
report_msg += "Temp: " +internal_sensor + " " + "C" + " "
report_msg += "S0: " +set_point_0 + " "
report_msg += "S1: " +set_point_1 + " "
report_msg += "S2: " +set_point_2 + " "
report_msg += "S3: " +set_point_3 + " "
report_msg += "I0: " +correction_factor_0 + " "
report_msg += "I1: " +correction_factor_1 + " "
report_msg += "I2: " +correction_factor_2 + " "
report_msg += "I3: " +correction_factor_3
report_msg += "\n"

# To screen for interactive use :
if input == "d" :
	if internal_sensor == "" or set_point_0 == "" or set_point_1 == "" or  \
	set_point_2 == "" or set_point_3 == "" or correction_factor_0 == "" or  \
	correction_factor_1 == "" or correction_factor_2 == "" or correction_factor_3 == "" :
		print ("Error reading haake values")
	else :
		print (report_msg)

# To separate files for the log (appending) and current values :
f_log = open('/home/supernemo/HaakeDL30Monitoring/HaakeValues_log.txt','a')
f_cur = open('/home/supernemo/HaakeDL30Monitoring/HaakeValues_cur.txt','w')
f_log.write(report_msg)
f_cur.write(report_msg)
