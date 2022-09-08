#!/usr/bin/python

import sys
import time
from time import sleep
sys.path.insert(0, "..")
from opcua import Client

# ------------------------------------------------------------- #
# Python script for manual readout from the client.
# Lauren Dawson, 20.05.2016
# ------------------------------------------------------------- #

if __name__ == "__main__":

	# Define client address
	client = Client("opc.tcp://sn-rpi1.holmbury.hep.ucl.ac.uk:48010/freeopcua/server")

	try:
		# Establish connection to client
		client.connect()

		# Fetch intial node
		root = client.get_root_node()

		# Get directory locations for all variables
		sensorData = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
		            "2:FG", "2:HaakeDL30", "2:SensorTemp", "2:SensorTemp_v"])

		tempCh0 = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
		            "2:FG", "2:Temperature", "2:Temp_Ch0", "2:Temp_Ch0_v"])

		tempCh1 = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
		            "2:FG", "2:Temperature", "2:Temp_Ch1", "2:Temp_Ch1_v"])

		# Set up while loop to read variables
		while True :
			# Create time stamp
			report_msg = ""
			date_msg = time.strftime("%d/%m/%y")
			time_msg = time.strftime("%H:%M:%S")
			report_msg = date_msg+" "+time_msg+" : "
				
			# Open files for writing
			f_sensor = open('/home/supernemo/ClientScripts/LogFiles/SensorTemp.txt','a')
    			f_t0 = open('/home/supernemo/ClientScripts/LogFiles/TempCh0.txt','a')
    			f_t1 = open('/home/supernemo/ClientScripts/LogFiles/TempCh1.txt','a')

    			# Get data value and print to text file
    			sensorTemp = sensorData.get_value()
    			print >> f_sensor, report_msg + str(sensorTemp)
    			f_sensor.close()

    			ch0Temp = tempCh0.get_value()
    			print >> f_t0, report_msg + str(ch0Temp)
    			f_t0.close()

    			ch1Temp = tempCh1.get_value()
    			print >> f_t1, report_msg + str(ch1Temp)
    			f_t1.close()

    			sleep(60)

    	finally:
    		client.disconnect()



