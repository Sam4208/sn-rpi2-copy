#!/usr/bin/python
import os
import subprocess
import argparse
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
# ------------------------------------------------------------- #
# Python script for reading the overall status of all devices.
# Lauren Dawson, 08.04.2016
# ------------------------------------------------------------- #
statusString = ""

#Insert options for t and d mode inputs
parser = argparse.ArgumentParser(description='Chose Readout Mode')
parser.add_argument('input', metavar='RO', type=str, choices = ['d', 't','temp','flow','haake','pres','lab'],
                   help='Desired Variable Readout')

args = parser.parse_args()
mode = args.input

# Readout temperatures from ADC:
if mode == 'd' or mode =='temp':
    #tempReadout = subprocess.check_output(['/home/supernemo/SVN/trunk/source/scripts/TempReadout2.py', 'd'])
    #print(tempReadout)
    print("Temperature: ")
    print("------------")

    tempReadout = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/TempReadout.py', 'd'], check=True, capture_output=True, text=True).stdout
    print(tempReadout)
    
    tempString = tempReadout
    #print(tempString)
    statusString += "Temperature: \n" + "----------- \n" +tempString + "\n"
    
   
elif mode == 't':
    print("Temperature: ")
    print("------------")
	

    tempReadouttest = subprocess.check_output(['/home/supernemo/SVN/trunk/source/scripts/TempReadout.py', 't'])
    tempStringtest = tempReadouttest.rstrip("\n")
    print(tempStringtest)
    statusString += "Temperature: \n" + "----------- \n" +tempStringtest + "\n"





# Readout flow rate information:
if mode == 'd' or mode=='flow':
    print("Flow Monitoring: ")
    print("----------------")



    flowReadout =subprocess.run(['/home/supernemo/FlowRateMonitoring/PR4000B.py', 'd'], check=True, capture_output=True, text=True).stdout
    flowString = flowReadout
    print(flowString)
    statusString += "Flow Monitoring: \n" + "---------------- \n" +flowString +"\n"
elif mode == 't':
    print("Flow Monitoring: ")
    print("----------------")



    flowReadouttest = subprocess.check_output(['/home/supernemo/FlowRateMonitoring/PR4000B.py', 't'])
    flowStringtest = flowReadouttest.rstrip("\n")
    print(flowStringtest)
    statusString += "Flow Monitoring: \n" + "---------------- \n" +flowStringtest +"\n"

# Readout values from Haake Bath:
if mode == 'd' or mode =='haake':

    print("Haake Values: ")

    print("-------------")


    haakeReadout =subprocess.run(['/home/supernemo/HaakeDL30Monitoring/HaakeValues.py', 'd'], check=True, capture_output=True, text=True).stdout
    haakeString = haakeReadout
    print(haakeString)
    statusString += "Haake Values: \n" + "------------- \n" +haakeString +"\n"
elif mode == 't':
    print("Haake Values: ")
 
    print("-------------")


    haakeReadouttest = subprocess.check_output(['/home/supernemo/HaakeDL30Monitoring/HaakeValues.py', 't'])
    haakeStringtest = haakeReadouttest.rstrip("\n")
    print(haakeStringtest)
    statusString += "Haake Values: \n" + "------------- \n" +haakeStringtest +"\n"

# Readout status of the Haake Bath:
if mode == 'd' or mode == 'haake':
    print("Haake Status: ")
    print("-------------")

    
    haakeStatusReadout = subprocess.run(['/home/supernemo/HaakeDL30Monitoring/OperatingStatus.py', 'd'], check=True, capture_output=True, text=True).stdout  
    haakeStatusString = haakeStatusReadout
    print(haakeStatusString)
    statusString += "Haake Status: \n" + "------------- \n" +haakeStatusString +"\n"
elif mode == 't':

    print("Haake Status: ")
    print("-------------")


    haakeStatusReadouttest = subprocess.check_output(['/home/supernemo/HaakeDL30Monitoring/OperatingStatus.py', 't'])
    haakeStatusStringtest = haakeStatusReadouttest.rstrip("\n")
    print(haakeStatusStringtest)
    statusString += "Haake Status: \n" + "------------- \n" +haakeStatusStringtest +"\n"

# Readout pressure:
if mode == 'd' or mode =='pres':
    print("Primary Bubbler Pressure: ")
    print("---------")
    
    pressureReadout = subprocess.run(['/home/supernemo/PressureMonitoring/EV94.py', 'd'], check=True, capture_output=True, text=True).stdout
    pressureString = pressureReadout
    
    print(pressureString)
    statusString += "Pressure: \n" + "--------- \n" +pressureString +"\n"
elif mode == 't':
    print("Primary Bubbler Pressure: ")
    print("---------")

    pressureReadouttest = subprocess.check_output(['/home/supernemo/PressureMonitoring/EV94.py','t'])
    pressureStringtest = pressureReadouttest.rstrip("\n")
    print(pressureStringtest)
    statusString += "Pressure: \n" + "--------- \n" +pressureStringtest +"\n"

# Readout Lab pressure and temperature
if mode == 'd' or mode =='lab':

	print("Lab Pressure and Temperature")
	print("----------------------------")

	cmd = 'ls /media/supernemo/P-76631/data | tail -n 1'
	#the cmd defines the command that would find the newest csv file for the lab temperature and pressure sensor
	list_csv = os.popen(cmd).read()
	print(list_csv)


	reader_file = '/home/supernemo/gcdc-b1100-reader-last-value'
	#the script Manu wrote for read the b1100 lab temperature and pressure
	run_file = '/media/supernemo/P-76631/data/'+str(list_csv).rstrip('\n')
	#the csv file feeds in the reader file, replaced with the search results from above, striped off the empty line
	tempReadout = subprocess.run([reader_file, run_file], check=True, capture_output=True, text=True).stdout
	print(tempReadout)


if mode == 'd':

# Check error status
	overallStatus = ""
	print ("Overall Status: ")
	print ("---------------")
#if mode == 't':
#	if 'Alarm' in haakeStatusStringtest :
#		overallStatus += "ALARM "
#	if 'Error' in tempStringtest or 'Error' in flowStringtest or 'Error' in haakeStringtest or 'Error' in pressureStringtest :
#       	overallStatus += "WARNING "
#
#elif mode == 'd':
#	if 'Alarm' in haakeStatusString :
#		overallStatus += "ALARM "
#	if 'Error' in tempString or 'Error' in flowString or 'Error' in haakeString or 'Error' in pressureString :
#		overallStatus += "WARNING "
#
#

	if overallStatus == "" :
		overallStatus += "GOOD"

	print (overallStatus)
	statusString += "Overall Status: \n" + "--------------- \n" +overallStatus +"\n"

	# To separate files for the log (appending) and current values :
	f_log = open('/home/supernemo/OverallStatus_log.txt','a')
	f_cur = open('/home/supernemo/OverallStatus_cur.txt','w')
	f_log.write(statusString)
	f_cur.write(statusString)
