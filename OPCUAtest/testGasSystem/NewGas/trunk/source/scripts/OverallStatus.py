#!/usr/bin/python

import subprocess

# ------------------------------------------------------------- #
# Python script for reading the overall status of all devices.
# Lauren Dawson, 08.04.2016
# ------------------------------------------------------------- #
statusString = ""

# Readout temperatures from ADC:
print "Temperature: "
print "-----------"
tempReadout = subprocess.check_output(['/home/supernemo/ADC_Monitoring/TempReadout.py', 'd'])
tempString = tempReadout.rstrip("\n")
print tempString
statusString += "Temperature: \n" + "----------- \n" +tempString + "\n"

# Readout flow rate information:
print "Flow Monitoring: "
print "----------------"
flowReadout = subprocess.check_output(['/home/supernemo/FlowRateMonitoring/PR4000B.py', 'd'])
flowString = flowReadout.rstrip("\n")
print flowString
statusString += "Flow Monitoring: \n" + "---------------- \n" +flowString +"\n"

# Readout values from Haake Bath:
print "Haake Values: "
print "-------------"
haakeReadout = subprocess.check_output(['/home/supernemo/HaakeDL30Monitoring/HaakeValues.py', 'd'])
haakeString = haakeReadout.rstrip("\n")
print haakeString
statusString += "Haake Values: \n" + "------------- \n" +haakeString +"\n"

# Readout status of the Haake Bath:
print "Haake Status: "
print "-------------"
haakeStatusReadout = subprocess.check_output(['/home/supernemo/HaakeDL30Monitoring/OperatingStatus.py', 'd'])
haakeStatusString = haakeStatusReadout.rstrip("\n")
print haakeStatusString
statusString += "Haake Status: \n" + "------------- \n" +haakeStatusString +"\n"

# Readout pressure:
print "Pressure: "
print "---------"
pressureReadout = subprocess.check_output(['/home/supernemo/PressureMonitoring/EV94.py','d'])
pressureString = pressureReadout.rstrip("\n")
print pressureString
statusString += "Pressure: \n" + "--------- \n" +pressureString +"\n"

# Check error status
overallStatus = ""
print "Overall Status: "
print "---------------"

if 'Alarm' in haakeStatusString :
	overallStatus += "ALARM "

if 'Error' in tempString or 'Error' in flowString or 'Error' in haakeString or 'Error' in pressureString :
	overallStatus += "WARNING "

if overallStatus == "" :
	overallStatus += "GOOD"

print overallStatus
statusString += "Overall Status: \n" + "--------------- \n" +overallStatus +"\n"

# To separate files for the log (appending) and current values :
f_log = open('/home/supernemo/OverallStatus_log.txt','a')
f_cur = open('/home/supernemo/OverallStatus_cur.txt','w') 
f_log.write(statusString)
f_cur.write(statusString)






