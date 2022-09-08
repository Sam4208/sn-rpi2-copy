#!/usr/bin/python

import subprocess
import serial as s
from time import sleep 

# ------------------------------------------------------------- #
# Python script for continuosly monitoring status of flow.
# Lauren Dawson, 11.05.2016
# Note that the unit has address "03" (default value ?)
# ------------------------------------------------------------- #

# Establish serial connection
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

# Read initial value
ser.write("@03?VL0\r")
# Clear buffer to help with lag :
ser.flush()

msg = ser.readline()
prevValue = msg.strip()

# Enter while loop
while True:
	# Read value again
	ser.write("@03?VL0\r")
	ser.flush()
	msg = ser.readline()
	newValue = msg.strip()

	if prevValue == 'ON' and newValue == 'OFF' :
		# Send email as flow rate has turned off
		subprocess.call("/home/supernemo/FlowRateMonitoring/SendEmail.sh")
		subprocess.call("/home/supernemo/FlowRateMonitoring/TurnOn.py d", shell = True)
		prevValue = newValue
		sleep(300)
	else :
		# Do not want a notification if flow has gone from OFF to ON, or has not changed
		prevValue = newValue
		sleep(300)