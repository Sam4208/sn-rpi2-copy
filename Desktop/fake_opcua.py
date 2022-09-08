from opcua import Server
import random
from random import randint
import datetime
import time

server = Server()

url="opc.tcp://127.0.0.1:4840"
server.set_endpoint(url)

name = "FAKE_OPCUA"
addspace = server.register_namespace(name)
#server.import_xml("Gas_System_testV3.xml")

node = server.get_objects_node()
#inital gas system
CMS = node.add_object(addspace,"CMS")
GAS_System = CMS.add_object(addspace,"GAS_System")
Monitoring = GAS_System.add_object(addspace,"Monitoring")
FG = Monitoring.add_object(addspace,"FG")
BP = Monitoring.add_object(addspace,"BP")
#FG objects
Haake = FG.add_object(2,"HaakeDL30")
Temp = FG.add_object(2,"Temperature")
S_temp = Haake.add_object(addspace,"SensorTemp")
T_Ch0 = Temp.add_object(addspace,"Temp_Ch0")
T_Ch1 = Temp.add_object(addspace,"Temp_Ch1")




SensorTemp_v = S_temp.add_variable(addspace,'SensorTemp_v',0)
Temp_Ch0_v = T_Ch0.add_variable(addspace,'Temp_Ch0_v',0)
Temp_Ch1_v = T_Ch1.add_variable(addspace,'Temp_Ch1_v',0)

#BP objects
BP_temp = BP.add_object(addspace,"Temperature")
BP_press = BP.add_object(addspace,"Pressure")
BP_flowrate = BP.add_object(addspace,"FlowRate")

T_Ch2 = BP_temp.add_object(addspace,"Temp_Ch2")
FR_Ch1 = BP_flowrate.add_object(addspace,"FlowRate_Ch1")
FR_Ch2 = BP_flowrate.add_object(addspace,"FlowRate_Ch2")

BP_press_v = BP_press.add_variable(addspace,"Pressure_v",0)
FR_Ch1_v = FR_Ch1.add_variable(addspace,"FlowRate_Ch1_v",0)
FR_Ch2_v = FR_Ch2.add_variable(addspace,"FlowRate_Ch2_v",0)
T_Ch2_v = T_Ch2.add_variable(addspace,"Temp_Ch2_v",0)


#set all writables

SensorTemp_v.set_writable()
Temp_Ch0_v.set_writable()
Temp_Ch1_v.set_writable()
BP_press_v.set_writable()
FR_Ch1_v.set_writable()
FR_Ch2_v.set_writable()
T_Ch2_v.set_writable()






server.start()


server.historize_node_data_change(SensorTemp_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(Temp_Ch0_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(Temp_Ch1_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(BP_press_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(FR_Ch1_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(FR_Ch2_v,period=datetime.timedelta(7),count=0)
server.historize_node_data_change(T_Ch2_v,period=datetime.timedelta(7),count=0)



print("server started at {}".format(url))
'''
SensorTemp_v_1= []
Temp_Ch0_v_1 = []
Temp_Ch1_v_1 = []
BP_press_v_1 = []
FR_Ch1_v_1 = []
FR_Ch2_v_1 = []
T_Ch2_v_1 = []
'''

while True:
    
    
    
	
	
	SensorTemp_v_1 = random.uniform(23,24)
	Temp_Ch0_v_1 = random.uniform(21,22)
	Temp_Ch1_v_1 = random.uniform(21,22)
	BP_press_v_1 = random.uniform(100,200)
	FR_Ch1_v_1 = random.uniform(9,11)
	FR_Ch2_v_1 = random.uniform(500,700)
	T_Ch2_v_1 = random.uniform(12,15)
	#timestamp = time.strftime("%y-%m-%d %H:%M:%S")
	#timestamp = datetime.datetime.utcnow()
	#print(timestamp)
	#report_msg_sensortemp = SensorTemp_v_1 + timestamp
	#print(SensorTemp_v_1,Temp_Ch0_v_1,Temp_Ch1_v_1,BP_press_v_1,FR_Ch1_v_1,FR_Ch2_v_1,T_Ch2_v_1)
	'''
	date_time = time.strftime("%d/%m/%y")
	current_time = time.strftime("%H:%M:%S")
	'''
	SensorTemp_v.set_value(SensorTemp_v_1)
	Temp_Ch0_v.set_value(Temp_Ch0_v_1)
	Temp_Ch1_v.set_value(Temp_Ch1_v_1)
	BP_press_v.set_value(BP_press_v_1)
	FR_Ch1_v.set_value(FR_Ch1_v_1)
	FR_Ch2_v.set_value(FR_Ch2_v_1)
	T_Ch2_v.set_value(T_Ch2_v_1)
	time.sleep(60)

