import ClientHistoryReadout as chis
import numpy as np
from datetime import timedelta
import datetime as dt
from email_alert import *




directory = '/home/supernemo/TemperatureLogs/New Logger Files/'

def path(variable):
    if variable == "SensorTemp":
        filename = (directory)+"SensorTemp.txt"
        dump_filename = (directory)+"SensorTemp_dump.txt"
    if variable == "Temp_Ch2":
        filename = (directory)+"Temp_Ch2.txt"
        dump_filename = (directory)+"Temp_Ch2_dump.txt"
    if variable == "Temp_Ch0":
        filename =(directory)+"Temp_Ch0.txt"
        dump_filename = (directory)+"Temp_Ch0_dump.txt"
    if variable == "Temp_Ch1":
        filename = (directory)+"Temp_Ch1.txt"
        dump_filename = (directory)+"Temp_Ch1_dump.txt"
        
    if variable == "Pressure":
        filename = (directory)+"Pressure.txt"
        dump_filename = (directory)+"Pressure_dump.txt"    
        
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
    data = chis.getHistory_duration(variable, 0.000278)
    variable , file ,dump_file = path(variable)
    #print(data)
    new_time, new_data = split(data)
    #print(new_time)
    #print(new_data)
    final_time = new_time[-1]
    final_data_raw = new_data[-1]
    
    #final_time = final_time_raw[0:25]
    final_data = round(final_data_raw,2)
    
    print(str(variable) +' timestamp: ' + str(final_time))
    print(str(variable) +' current value: ' + str(final_data))
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
    
        
        
    
    #print(last_temp)
    #print(last_time)
        
    return last_temp, last_time

def dump_file_avg(variable):
    readin = []
    variable , file ,dump_file = path(variable)
    with open(dump_file,'r') as f:
  
        lines = f.readlines()
        for i in range(len(lines)):
            line_single = lines[i]
            
            temp = line_single[47:55]
          
            readin.append(float(temp))
        avg = np.average(readin)
  
    print(str(variable) + ' average short term value: '+ str(avg))
    return avg

def dump_file_open(variable):
   
    variable , file ,dump_file = path(variable)
    f = open(dump_file,'r+')
    lines = f.readlines()[-1]
    
    last_lines = str(lines)
    
    last_unchange_time = last_lines[11:36]
    last_unchange_temp = last_lines[47:55]
    
        
        
    return last_unchange_temp, last_unchange_time

def read_in_threshold_file(variable):
    f = open(str(directory)+"log_system_settings.txt", "r")
    line_text_from_file = f.read().splitlines()  

    for line in range (0,len((line_text_from_file))):
        if line_text_from_file[line] == variable:
            short_term_upper_trigger = float(line_text_from_file[line+1][25:27])
            short_term_lower_trigger = float(line_text_from_file[line+2][25:27])
        elif variable == 'ethanol' and line_text_from_file[line] == 'FGT1 FGT0 Temperature Difference Trigger':
            print(line_text_from_file[line+1][0:3])
            short_term_upper_trigger,short_term_lower_trigger = float(line_text_from_file[line+1][1:3]),float(line_text_from_file[line+1][1:3])
            
    f.close()
    
    return short_term_upper_trigger,short_term_lower_trigger

def compare(threshold_1,variable):
    
    
    
    avg = dump_file_avg(variable)
    last_temp,last_time = file_open(variable)
    final_time,final_data = get_last_datapoint(variable)
    
    trigger_short_term_average ='no'
    trigger_bound ='no'
  
    
    #print(threshold_1)
    compare = avg - float(final_data)
    if abs(compare) >= threshold_1:
        trigger_short_term_average ='yes'
        
        
    short_term_upper_threshold,short_term_lower_threshold = read_in_threshold_file(variable)
  
    
    if final_data > short_term_upper_threshold or final_data < short_term_lower_threshold :
        trigger_bound ='yes'
  
    
    else:
        pass
    
    
    
  
    return trigger_short_term_average,trigger_bound,last_temp,last_time,final_time,final_data 


def clear_file(file):
    with open(file,'r') as f:
        line_number = 1
        lines=f.readlines()
    
        with open(file,'w') as f_2:
        

            for line in lines:
            
                if line_number != 1 :
                    #print(line)
                    f_2.write(line)
                if line_number == 11:
                    f_2.write(line.strip('\n'))
                line_number += 1
    f_2.close()
    f.close()

def automated_logger_time():

    start = dt.time(14, 33, 0)
    end = dt.time(14, 35, 0)
    current = dt.datetime.now().time()
    
    return start <= current <= end

def ch0_ch1_comparison(variable,last_temp):
    ethanol_alert=False
   
    if variable=="Temp_Ch0":
        last_temp_ch0 = float(last_temp)
        print('c0checkked')
    elif variable=="Temp_Ch1":
        print('c1checkked')
        last_temp_ch1 = float(last_temp)
        ethanol_bound,ethanol_bound=read_in_threshold_file('ethanol')
        print(last_temp_ch0-last_temp_ch1)
        if last_temp_ch0-last_temp_ch1 < ethanol_bound:
            ethanol_alert = True
    
    return ethanol_alert,last

def write_file(threshold,variable):
    variable , filename , dump_file = path(variable)
    
    f = open(filename,'a')
    f_2 = open(dump_file,'a')
 
    warn_sense = False
    warn_0 = False
    warn_1 = False
    warn_2 = False
    warn_p = False
 
    activate_alert = False
    trigger_short_term_average,trigger_bound,last_temp,last_time,final_time,final_data = compare(threshold,variable)
    
    ethanol_alert=ch0_ch1_comparison(variable,last_temp)
    
    if trigger_short_term_average == 'no':
        
        clear_file(dump_file)
        f_2.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
     
        
        print(variable + ' checked'+str('\n----------------------------------'))
        
    if trigger_short_term_average == 'yes' or trigger_bound =='yes' or automated_logger_time()==True or ethanol_alert ==True:
        
        last_unchange_temp , last_unchange_time =  dump_file_open(variable)
        f.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
        
        clear_file(dump_file)
        f_2.write("Date/Time: {} Temp(C): {}\n".format(final_time, final_data))
        print(variable + ' changed,logged in ' + filename+str('\n----------------------------------'))
        
    if trigger_bound == 'yes' or ethanol_alert == True:
       
        activate_alert = True
        
        if variable =="SensorTemp":
                warn_sense = True 
        elif variable =="Temp_Ch0":
                warn_0 = True 
        elif variable =="Temp_Ch1":
                warn_1 = True 
        elif variable =="Temp_Ch2":
                warn_2 = True
        elif variable =="Pressure":
                warn_p = True
        elif ethanol_alert ==True:
            warn_0 = True
            warn_1 = True 
            
                
    return activate_alert,warn_sense,warn_0,warn_1,warn_2,warn_p,ethanol_alert

list_name = []
threshold = []


f = open(str(directory)+"variable_threshold.txt",'r+')
lines = f.readlines()


for i in range (len(lines)) :
    name_1 , value = lines[i].split()
    
    list_name.append(name_1)
    threshold.append(value)
print(list_name)
activate_alert_final = False
warn_sense_final = False
warn_0_final=False
warn_1_final=False
warn_2_final=False
warn_p_final=False
ethanol_alert_final=False

for i in range (len(list_name)): 
  activate_alert, warn_sense, warn_0, warn_1,warn_2,warn_p,ethanol_alert =  write_file(float(threshold[i]),list_name[i])
  
  if activate_alert == True:
      activate_alert_final =True
  if  warn_sense==True:
      warn_sense_final=True
  if  warn_0==True:
      warn_0_final=True
  if  warn_1==True:
      warn_1_final=True   
  if  warn_2==True:
      warn_2_final=True
  if  warn_p==True:
      warn_p_final=True
  if ethanol_alert ==True:
      ethanol_alert_final=True
      
      
print('\nAlerts:\nSensorTemp: '+str(warn_sense_final)+'\nCh0: '+str(warn_0_final)+'\nCh1: '+str(warn_1_final)+'\nCh2: '+str(warn_2_final)+'\nPressure: '+str(warn_p_final)+'\nEthanol Comparison: '+str(ethanol_alert_final))


if activate_alert_final == True:
    print('\nSending Alert Email')
    email_alert(True,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,ethanol_alert_final)
else:
    print('No Email Alert Sent')
#print('Email Sent:'+str(activate_alert_final))
