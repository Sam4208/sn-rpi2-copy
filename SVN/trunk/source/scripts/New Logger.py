import subprocess
import numpy as np
from datetime import timedelta
import datetime as dt
from email_alert import *


automated_logger_time_set=[22,30,0] # hour,minute,second

directory = '/home/supernemo/TemperatureLogs/New Logger Files/'

def path(variable):

     
    filename = (directory)+str(variable)+".txt"
    dump_filename = (directory)+str(variable)+"_dump.txt"    
        
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


def variable_status(variable):

        if variable == 'Water_Bath':
            variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/HaakeValues.py','T'], check=True, capture_output=True, text=True).stdout

        if variable == 'FGT1':
            variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/TempReadout.py','FGT1'], check=True, capture_output=True, text=True).stdout


        if variable == 'FGT2':
              variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/TempReadout.py','FGT2'], check=True, capture_output=True, text=True).stdout

        if variable =='BPT':

             variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/TempReadout.py','BPT'], check=True, capture_output=True, text=True).stdout


        if variable =='Pressure':

               variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/EV94.py','0'], check=True, capture_output=True, text=True).stdout

        if variable == 'FRHe':
  
             variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/PR4000B.py','FR1'], check=True, capture_output=True, text=True).stdout
  
    
        if  variable == 'FRAr':
          
           variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/PR4000B.py','FR2'], check=True, capture_output=True, text=True).stdout


        return float(variable_output)


def get_current_datapoint(variable):
    data = variable_status(variable)
    time = dt.datetime.now()
    
    if variable=='Water_Bath' and data == float(999):
       data = 'Chiller off'

    print(str(variable) +' timestamp: ' + str(time))
    print(str(variable) +' current value: ' + str(data))

    return time, data

def dump_file_avg(variable):
    readin = []
    variable , file ,dump_file = path(variable)
    with open(dump_file,'r') as f:
        
        lines = f.readlines()
        for i in range(len(lines)):
            line_single = lines[i]
            
            temp = line_single[30:38]
            if temp =='2022-11-29 12:36:53.209280 -- Chiller off'[30:38]:
                temp =  float(0)
            readin.append(float(temp))
        avg = np.average(readin)
  
    print(str(variable) + ' average short term value: '+ str(avg))
    return avg

def log_file_open(variable):
    
    variable , file ,dump_file = path(variable)
    f = open(file,'r+')
    lines = f.readlines()[-1]
    
    last_lines = str(lines)
    
    last_log_time = last_lines[0:20]
    last_log_value = last_lines[30:38]
    
        
        
    return last_log_value, last_log_time

def compare(variable_settings,variable,chiller_status):
    
    short_term_average_bound = variable_settings[0]

    if chiller_status=='off':
       upper_trigger = variable_settings[2]
       lower_trigger = variable_settings[3] 
    elif chiller_status=='on':
       upper_trigger = variable_settings[4]
       lower_trigger = variable_settings[5] 
    
    avg = dump_file_avg(variable)
    last_log_value,last_log_time = log_file_open(variable)
    current_time,current_value = get_current_datapoint(variable)
    
    trigger_short_term_average ='no'
    trigger_bound ='no'
    chiller_off_alert = 'no'

    if variable =='Water_Bath' and chiller_status=='off':  
       
       if (last_log_value) == '2022-11-29 12:36:53.209280 -- Chiller off'[30:38]:
             chiller_off_alert = 'no'
            
             
       else:
            chiller_off_alert = 'yes'
    else:

      compare = avg - float(current_value)
      if abs(compare) >= short_term_average_bound:
         trigger_short_term_average ='yes'
        
      if current_value > upper_trigger or current_value < lower_trigger :

              
              trigger_bound ='yes'
  
    
      else:
          pass
    
    
    
  
    return trigger_short_term_average,trigger_bound,current_time,current_value,chiller_off_alert 


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
    hour = automated_logger_time_set[0]
    minute = automated_logger_time_set[1]
    second = automated_logger_time_set[2]


    start = dt.time(hour, minute, second)
    end = dt.time(hour, minute+11, second)

    current = dt.datetime.now().time()
    
    return start <= current <= end

def ch0_ch1_comparison(last_temp_ch0,last_temp_ch1,ethanol_bound):
        ethanol_alert=False
        if last_temp_ch0-last_temp_ch1 < ethanol_bound:
            ethanol_alert = True
    
        return ethanol_alert

def write_file(variable_settings,variable,chiller_status):
    variable , filename , dump_file = path(variable)
    
    f = open(filename,'a')
    f_2 = open(dump_file,'a')
 
    trigger_short_term_average,trigger_bound,current_time,current_value,chiller_off_alert = compare(variable_settings,variable,chiller_status)
    
  
    if trigger_short_term_average == 'no' and chiller_off_alert=='no':
        
        clear_file(dump_file)
        f_2.write("{} -- {}\n".format(current_time, current_value))

        print(variable + ' checked, change not logged'+str('\n----------------------------------'))
        
    if trigger_short_term_average == 'yes' or trigger_bound =='yes' or automated_logger_time()==True or chiller_off_alert =='yes':
        
        
        f.write("{} -- {}\n".format(current_time, current_value))
        
        clear_file(dump_file)
        f_2.write("{} -- {}\n".format(current_time, current_value))

        print(variable + ' changed,logged in ' + filename+str('\n----------------------------------'))

    warn_sense = False
    warn_0 = False
    warn_1 = False
    warn_2 = False
    warn_p = False
    warn_FRHe = False
    warn_FRAr = False 
    activate_alert = False
        
    if chiller_off_alert == 'yes':
           activate_alert = True

    if trigger_bound == 'yes' :
       
        activate_alert = True
    
        if variable =="Water_Bath":
                warn_sense = True 
        elif variable =="FGT1":
                warn_0 = True 
        elif variable =="FGT2":
                warn_1 = True 
        elif variable =="BPT":
                warn_2 = True
        elif variable =="Pressure":
                warn_p = True
        elif variable =="FRAr":
                warn_FRAr = True
        elif variable =="FRHe":
                warn_FRHe = True
            
                
    return activate_alert,warn_sense,warn_0,warn_1,warn_2,warn_p,warn_FRHe,warn_FRAr,current_value,chiller_off_alert



def alert_status_print(warn):
     if warn == True:
         status = 'Warning'
     else:
        status = 'OK'

     return status 

def get_log_settings(variable):

   f = open(str(directory)+"log_system_settings.txt",'r+')
   lines = f.read().splitlines()  
   for line in range (0,len(lines)):
       if str(lines[line]) == variable:
         short_term_average_bound = float(lines[line+1][25:29])
         medium_term_average_bound = float(lines[line+2][26:30])
         chiller_off_upper_trigger = float(lines[line+3][26:30])
         chiller_off_lower_trigger = float(lines[line+4][26:30])
         chiller_on_upper_trigger = float(lines[line+5][25:29])
         chiller_on_lower_trigger = float(lines[line+6][25:29])

       if str(lines[line]) == "FGT1 FGT0 Temperature Difference Trigger":
         ethanol_bound = float(lines[line+1][0:5])

   variable_settings = [short_term_average_bound,medium_term_average_bound,chiller_off_upper_trigger,chiller_off_lower_trigger,chiller_on_upper_trigger,chiller_on_lower_trigger]

   return variable_settings,ethanol_bound


activate_alert_final = False
warn_sense_final = False
warn_0_final=False
warn_1_final=False
warn_2_final=False
warn_p_final=False
ethanol_alert_final=False
warn_FRHe_final = False
warn_FRAr_final = False
chiller_off_alert_final = False

variables = ['Water_Bath','FGT1','FGT2','BPT','Pressure','FRHe','FRAr']

if variable_status('Water_Bath')==float(999):
    chiller_status = 'off'
else:
    chiller_status = 'on'

for i in range (0, len(variables)):
  
  variable_settings,ethanol_bound = get_log_settings(variables[i]) 
  activate_alert, warn_sense, warn_0, warn_1,warn_2,warn_p,warn_FRHe,warn_FRAr,current_value,chiller_off_alert =  write_file(variable_settings,variables[i],chiller_status)
 
  if variables[i]=='FGT1':
       temp_ch0_value = current_value
  if variables[i]=='FGT2':
       temp_ch1_value = current_value
       ethanol_alert_final= ch0_ch1_comparison(temp_ch0_value,temp_ch1_value,ethanol_bound)

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
  if  warn_FRHe==True:
      warn_FRHe_final=True
  if  warn_FRAr==True:
      warn_FRAr_final=True
  if chiller_off_alert == 'yes':
     chiller_off_alert_final = True
           
print('\nAlerts:\nWater Bath: '+alert_status_print(warn_sense_final)+'\nFGT1: '+alert_status_print(warn_0_final)+'\nFGT2: '+alert_status_print(warn_1_final)+'\nBPT: '+alert_status_print(warn_2_final)+'\nFlowrate He: '+alert_status_print(warn_FRHe_final)+'\nFlowrate Ar: '+alert_status_print(warn_FRAr_final)+'\nPressure: '+alert_status_print(warn_p_final)+'\nFGT1 FGT2 Temperature Difference: '+alert_status_print(ethanol_alert_final))

if activate_alert_final == True or ethanol_alert_final:
    print('\nSending Alert Email')
    email_alert(True,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final)

elif automated_logger_time() ==True:
    print('\nSending daily update email')
    email_alert(True,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final)


else:
    print('No Email Alert Sent')
#print('Email Sent:'+str(activate_alert_final))

