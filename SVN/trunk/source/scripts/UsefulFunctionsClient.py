#!/usr/bin/python

import sys
import time
from time import sleep
sys.path.insert(0, "..")
from opcua import Client
from opcua import ua
from datetime import timedelta
import datetime
import fcntl
import errno

# ------------------------------------------------------------------------------------------ #
# Python script containing useful functions for reading history of variabes from the client.
# Lauren Dawson, 13.07.2016
# ------------------------------------------------------------------------------------------ #
def connect_client() :

    client = Client("opc.tcp://127.0.0.1:4840")
    #client = Client("opc.tcp://localhost:48010/freeopcua/server")
    # For MSSL opc.tcp://sn-rpi1.holmbury.hep.ucl.ac.uk:48010/freeopcua/server"


    # Initialise counting variable
    attempts = 0

    while True :
            try :
                attempts +=1
                if attempts > 60 :
                    print ("Error connecting - too many attempts")
                    sys.exit(1)
                else :
                    time.sleep(1)
                    print ("Connecting")
                    client.connect()
                    break
            except :
            # raise on unrelated IOErrors
                print ("Error connecting")
                time.sleep(1)

    return client

def retrieve_variable_path(root, variable) :

	# Get directory locations for all variables
	if variable == "SensorTemp" :
		sensorData = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring", 
	    	        "2:FG", "2:HaakeDL30", "2:SensorTemp", "2:SensorTemp_v"])
		return sensorData
	elif variable == "Pressure" :	
		pressureData = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:BP", "2:Pressure", "2:Pressure_v"]) 
		return pressureData
	elif variable == "FlowRate_Ch1" :
		flowRateCh1Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:BP", "2:FlowRate", "2:FlowRate_Ch1", "2:FlowRate_Ch1_v"])
		return flowRateCh1Data
	elif variable == "FlowRate_Ch2" :
		flowRateCh2Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:BP", "2:FlowRate", "2:FlowRate_Ch2", "2:FlowRate_Ch2_v"])
		return flowRateCh2Data
	elif variable == "Temp_Ch2" :
		tempCh2Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:BP", "2:Temperature", "2:Temp_Ch2", "2:Temp_Ch2_v"])
		return tempCh2Data
	elif variable == "Temp_Ch0" :
		tempCh0Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:FG", "2:Temperature", "2:Temp_Ch0", "2:Temp_Ch0_v"])
		return tempCh0Data
	elif variable == "Temp_Ch1" :
		tempCh1Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
					"2:FG", "2:Temperature", "2:Temp_Ch1", "2:Temp_Ch1_v"])
		return tempCh1Data

def retrieve_data_for_variable_time_window(variable, start, end):
    
    client = Client("opc.tcp://127.0.0.1:4840")
	#client = Client("opc.tcp://localhost:48010/freeopcua/server")

	# Establish connection to client
    client.connect()

    # Fetch intial node
    root = client.get_root_node()

    # Get path to variable
    path = retrieve_variable_path(root, variable)

    #history = []

    # Fill array with history in requested time slot
    history = path.read_raw_history(start, end)
   
    client.disconnect()
    
    return history

def retrieve_data_for_variable_hours(variable, duration):
    
    client = Client("opc.tcp://127.0.0.1:4840")
    #client = Client("opc.tcp://localhost:48010/freeopcua/server")

    client.connect()

    # Fetch intial node
    root = client.get_root_node()

    path = retrieve_variable_path(root, variable)

    history = []

    # DSW, 08.09.16 : note that utcnow() is correct, since the MOS server times
    # are in UTC (I think).
    end_time = datetime.datetime.utcnow()
    start_time = end_time - timedelta(hours = duration)
    history.append(path.read_raw_history(start_time, end_time))
#     print(history)
    client.disconnect()
    
    return history

#retrieve_data_for_variable_hours("Pressure", 1)

