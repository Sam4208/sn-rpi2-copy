import ClientHistoryReadout as chis
import numpy as np
from datetime import timedelta
import datetime as dt







def path(variable):
    if variable == "SensorTemp":
        filename = "/home/supernemo/TemperatureLogs/SensorTemp.txt"
        dump_filename = "/home/supernemo/TemperatureLogs/SensorTemp_dump.txt"
    if variable == "Temp_Ch2":
        filename = "/home/supernemo/TemperatureLogs/Temp_Ch2.txt"
        dump_filename = "/home/supernemo/TemperatureLogs/Temp_Ch2_dump.txt"
    if variable == "Temp_Ch0":
        filename ="/home/supernemo/TemperatureLogs/Temp_Ch0.txt"
        dump_filename = "/home/supernemo/TemperatureLogs/Temp_Ch0_dump.txt"
    if variable == "Temp_Ch1":
        filename = "/home/supernemo/TemperatureLogs/Temp_Ch1.txt"
        dump_filename = "/home/supernemo/TemperatureLogs/Temp_Ch1_dump.txt"
    return variable , filename , dump_filename
    
def split(data):
    dates = data[0::2]
    datapoints = data[1::2]

    for i in range(len(datapoints)):
        datapoint = datapoints[i].replace("'","")
        datapoints[i] = float(datapoint)

    for i in range(len(dates)):
        dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f)")
        # originally dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f") the test server have a extra ) at the end of timestamp for some reason.

    return dates, datapoints

def get_last_datapoint(variable):
    data = chis.getHistory_duration(variable, 0.017)
    #print(data)
    new_time, new_data = split(data)
    #print(new_time)
    #print(new_data)
    final_time = new_time[-1]
    final_data_raw = new_data[-1]
    
    #final_time = final_time_raw[0:25]
    final_data = round(final_data_raw,2)
    
    print (final_time)
    print (final_data)
    return final_time, final_data

def file_open(variable):
    #print(index)
    variable , file ,dump_file = path(variable)
    f = open(file,'r')
    lines = f.readlines()[-1]
    #print(lines)
    last_lines = str(lines)
    
    last_time = last_lines[11:31]
    last_temp = last_lines[47:52]
    
        
        
    
    print(last_temp)
    print(last_time)
        
    return last_temp, last_time

def dump_file_open(variable):
    #print(index)
    variable , file ,dump_file = path(variable)
    f = open(dump_file,'r+')
    lines = f.readlines()[-1]
    #print(lines)
    last_lines = str(lines)
    
    last_unchange_time = last_lines[11:36]
    last_unchange_temp = last_lines[47:55]
    
        
        
    
    #print(last_temp)
    #print(last_time)
        
    return last_unchange_temp, last_unchange_time

def compare(threshold_1,variable):
    
    
    last_temp,last_time = file_open(variable)
    final_time,final_data = get_last_datapoint(variable)
    status = 'no'
    print(threshold_1)
    compare = float(last_temp) - float(final_data)
    if abs(compare) >= threshold_1:
        status ='yes'
    else:
        pass
    #print(compare)
    
    #print(status)
    return status





def write_file(threshold,variable):
    variable , filename , dump_file = path(variable)
    
    f = open(filename,'a')
    f_2 = open(dump_file,'r+')
    
    status = compare(threshold,variable)
    last_temp,last_time = file_open(variable)
    final_time,final_data = get_last_datapoint(variable)
    print(status)
    if status == 'no':
        f_2.truncate(0)
        f_2.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
        #f.write("Date/Time: {} checked".format(final_time))
        #f.write("\nDate/Time: {} Temp(C): {}\n".format(final_time, final_data))
        
        print(variable + ' checked')
    if status == 'yes':
        last_unchange_temp , last_unchange_time =  dump_file_open(variable)
        
        f.write("Date/Time: {} Temp(C): {}\n".format(last_unchange_time, last_unchange_temp))
        f.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
        f_2.truncate(0)
        f_2.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
        print(variable + ' changed,logged in ' + filename)
        
        
#list_name = ["SensorTemp","Temp_Ch2","Temp_Ch0","Temp_Ch1"]
#threshold = ['2','0','2','0']

list_name = []
threshold = []


f = open("/home/supernemo/TemperatureLogs/variable_threshold.txt",'r+')
#lines = f.readlines()

lines = f.readlines()
#print(lines)

for i in range (4) :
    name_1 , value = lines[i].split()
    
    list_name.append(name_1)
    threshold.append(value)
    '''
    path(name_1)
    get_last_datapoint(name_1)
    file_open(name_1)
    compare(float(value),name_1)
    write_file(float(value),name_1)
    
    

#print(list_name)
#print(threshold)
'''
for i in range (len(list_name)):
    #print(list_name[i])
    
    path(list_name[i])
    get_last_datapoint(list_name[i])
    file_open(list_name[i])
    #print(threshold[i])
    compare(float(threshold[i]),list_name[i])
    write_file(float(threshold[i]),list_name[i])
