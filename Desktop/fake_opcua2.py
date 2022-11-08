from opcua import Server
import random
from random import randint
import datetime
import time
import numpy as np

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
counter = 0


year = 2021
year2 = 2021

month=11
month2=11

day=15
day2 = 30

hour=0
hour2=0

min_=0
min_2=0

second=0
second2=0

milisecond=0
milisecond2=0


def plot_temp_data(input_file,title):


    
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    precision = 5
    
    no_events = int(len(lines)/precision)
    
    for i in range(0,no_events):
        i = i* precision
        temp_add = (lines[i][47:56])
        
        try:
            float(temp_add)
            time_add = datetime.datetime(int(lines[i][11:15]),int(lines[i][16:18]),int(lines[i][19:21]),int(lines[i][22:24]),int(lines[i][25:27]),int(lines[i][28:30]),int(lines[i][31:38]))
            temp_add = float(temp_add)
           # print(time_add,datetime.datetime(year, month, day,hour,min_,second,milisecond))
            if time_add > datetime.datetime(year,month,day,hour,min_,second,milisecond) and time_add<datetime.datetime(year2,month2,day2,hour2,min_2,second2,milisecond2):
            
               
                time = np.append(time,time_add)
                temp = np.append(temp,temp_add)
            
        except ValueError:
            continue
            #print('error- temp: '+str(temp_add)+'     time:'+str(time_add))
            
        
    return time,temp
  
# Creating axis
# add_axes([xmin,ymin,dx,dy])

  




time0,temp0=plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch0.txt','FGT1')
time1,temp1=plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch1.txt','FGT0')
time2,temp2=plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch2.txt','BPT2')
#timesen,tempsen=plot_temp_data('/home/supernemo/TemperatureLogs/SensorTemp.txt','BPT2')
#plot_temp_data('Gas-system code library/TemperatureLogs/SensorTemp.txt',ax4)




while True:
    
    
    
	
	
	SensorTemp_v_1 = random.uniform(12,13)
	Temp_Ch0_v_1 = random.uniform(12,12.7)
	Temp_Ch1_v_1 = random.uniform(12.5,13)
	BP_press_v_1 = random.uniform(1,2)
	FR_Ch1_v_1 = random.uniform(1,2)
	FR_Ch2_v_1 = random.uniform(0.001,0.002)
	T_Ch2_v_1 = random.uniform(23,25)
	
	
	Temp_Ch0_v_1 = temp0[counter]
	Temp_Ch1_v_1 = temp1[counter]
	T_Ch2_v_1    = temp2[counter]
	#T_Ch2_v_1    = tempsen[counter]
	
	
	
	
	
	
	
	#timestamp = time.strftime("%y-%m-%d %H:%M:%S")
	#timestamp = datetime.datetime.utcnow()
	#print(timestamp)
	#report_msg_sensortemp = SensorTemp_v_1 + timestamp
	print(SensorTemp_v_1,Temp_Ch0_v_1)
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
	counter += 1
	time.sleep(0.5)

