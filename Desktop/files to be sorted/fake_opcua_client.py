from opcua import Client
import time
import datetime
from datetime import timedelta
from opcua import Client
from opcua import ua
#url = "opc.tcp://172.1.18.230:48010/freeopcua/server"
url = "opc.tcp://localhost:48010/freeopcua/server"
#url = 'opc.tcp://127.0.0.1:4840'
client=Client(url)

client.connect()
print("Client connected")

while True:
    
    root = client.get_root_node()
    sensorData = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring", 
                    "2:FG", "2:HaakeDL30", "2:SensorTemp", "2:SensorTemp_v"])
    tempCh0 = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring", 
                    "2:FG", "2:Temperature", "2:Temp_Ch0", "2:Temp_Ch0_v"])
    tempCh1 = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring", 
                    "2:FG", "2:Temperature", "2:Temp_Ch1", "2:Temp_Ch1_v"])
    pressureData = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
                    "2:BP", "2:Pressure", "2:Pressure_v"])
    flowRateCh1Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
                    "2:BP", "2:FlowRate", "2:FlowRate_Ch1", "2:FlowRate_Ch1_v"])
    flowRateCh2Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
                    "2:BP", "2:FlowRate", "2:FlowRate_Ch2", "2:FlowRate_Ch2_v"])
    tempCh2Data = root.get_child(["0:Objects", "2:CMS", "2:GAS_System", "2:Monitoring",
                    "2:BP", "2:Temperature", "2:Temp_Ch2", "2:Temp_Ch2_v"])
    
    
    duration = 1
    end_time = datetime.datetime.utcnow()
    #start_time = datetime.datetime.utcnow()
    start_time = end_time - timedelta(seconds = duration)
    
    
    sensor = sensorData.get_value()
    
    
    temp0 = tempCh0.get_value()
    temp1 = tempCh1.get_value()
    pressure_bp = pressureData.get_value()
    fr_1 = flowRateCh1Data.get_value()
    fr_2 = flowRateCh2Data.get_value()
    temp2 = tempCh2Data.get_value()
    
    #dataSample = readHistory(uaClient,tempCh2Data,datetime('now')-seconds(30),datetime('now'))
    #print(dataSample)
    temp3 = tempCh2Data.read_raw_history(start_time,end_time,10)
    print(temp3)
    print(temp2)

    
    #print("sensor temperature is ",sensor)
    '''
    print("FG 1 temperature is ",temp0)
    print("FG 2 temperature is ",temp1)
    print("BP pressure is ",pressure_bp)
    print("Flowrate channel 1 is ",fr_1)
    print("Flowrate channel 2 is ",fr_2)
    print("BP temperature is ",temp2)
	'''
    time.sleep(1)

