import subprocess
import numpy as np
from datetime import timedelta
import datetime as dt
from gas_system_useful_functions import *

automated_email_time_set=[8,30,0] # hour,minute,second

directory = '/home/supernemo/TemperatureLogs/New Logger Files/'

def path(variable):

     
    log_filename = (directory)+str(variable)+".txt"
    short_term_log_filename = (directory)+str(variable)+"_short_term_rolling_log.txt"    
    medium_term_log_filename = (directory)+str(variable)+"_med_term_rolling_log.txt"


    return log_filename,short_term_log_filename,medium_term_log_filename
    
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

    else:
        data = (round(data,3))


    print(str(variable) +' timestamp: ' + str(time))
    print(str(variable) +' current value: ' + str(data))

    return time, data

def rolling_log_file_avg(term,variable):
    readin = []
    log_file ,short_log_file,med_log_file = path(variable)
    if term == 'short':
        file_to_open = short_log_file
    if term == 'med':
        file_to_open = med_log_file
    
    with open(file_to_open,'r') as f:
        
        lines = f.readlines()
        for i in range(len(lines)):
            line_single = lines[i]
            
            value = line_single[30:38]
            if value =='2022-11-29 12:36:53.209280 -- Chiller off'[30:38]:
                value =  float(0)
            readin.append(float(value))
        avg = np.average(readin)
  
    print(str(variable) + ' average short term value: '+ str(avg))
    return avg

def compare_subfunction(current_value,term,variable_settings,variable):
 
    if term=='short': 
         term_average_bound = variable_settings[0]
    if term=='med': 
         term_average_bound = variable_settings[1]

    trigger_term_average ='no'
    avg= rolling_log_file_avg(term,variable)
    compare = avg - float(current_value)
    if abs(compare) >= term_average_bound:
         trigger_term_average ='yes'

    return trigger_term_average



def compare_rolling_averages_to_current_value(variable_settings,variable,chiller_status):


    log_file,short_log_file,med_log_file = path(variable)
    
    short_term_average_bound = variable_settings[0]
    medium_term_average_bound = variable_settings[1]
    if chiller_status=='off':
       upper_trigger = variable_settings[2]
       lower_trigger = variable_settings[3] 
    elif chiller_status=='on':
       upper_trigger = variable_settings[4]
       lower_trigger = variable_settings[5] 
    
    current_time,current_value = get_current_datapoint(variable)
    last_log_time,last_log_value = get_last_value_time_from_log(log_file)
    last_short_log_time,last_short_log_value, = get_last_value_time_from_log(short_log_file)

    trigger_short_term_average = 'no'
    trigger_med_term_average = 'no'   
    trigger_bound ='no'
    chiller_off_alert = 'no'

    if variable =='Water_Bath' and chiller_status=='off':  
       
       if (last_log_value) == 'Chiller off':
             chiller_off_alert = 'no'
             
       else:
            chiller_off_alert = 'yes'
    else:

      trigger_short_term_average = compare_subfunction(current_value,'short',variable_settings,variable)
      trigger_med_term_average   = compare_subfunction(current_value,'med',variable_settings,variable)
      if current_value > upper_trigger or current_value < lower_trigger:
         current_time,current_value = get_current_datapoint(variable)
         if current_value > upper_trigger or current_value < lower_trigger:
                 trigger_bound ='yes'

      else:
            pass
    
    
    
  
    return trigger_short_term_average,trigger_med_term_average,trigger_bound,current_time,current_value,chiller_off_alert,last_log_time,last_short_log_time,last_short_log_value 


def clear_file(log_file):
    with open(log_file,'r') as f:
        line_number = 1
        lines=f.readlines()
    
        with open(log_file,'w') as f_2:
        

            for line in lines:
            
                if line_number != 1 :
                    #print(line)
                    f_2.write(line)
                if line_number == 11:
                    f_2.write(line.strip('\n'))
                line_number += 1
    f_2.close()
    f.close()

def automated_email_time():
    hour = automated_email_time_set[0]
    minute = automated_email_time_set[1]
    second = automated_email_time_set[2]


    start = dt.time(hour, minute, second)
    end = dt.time(hour, minute+2, second)

    current = dt.datetime.now().time()
    
    return start <= current <= end


def automated_logger_time():
  current = dt.datetime.now().time()
  if current.minute>0 and current.minute<3 and current.hour%2 == 0:

    log=True
  
  else:

    log=False
  
  return log

def write_alert_record(current_time,warn_1,warn_2,warn_3,warn_4,warn_5,warn_6,warn_7,warn_8,warn_9,file):

       f = open(directory+str(file)+'_alert_record.txt','w')
       f.write("{} {}{}{}{}{}{}{}{}{}\n".format(current_time,int(warn_1),int(warn_2),int(warn_3),int(warn_4),int(warn_5),int(warn_6),int(warn_7),int(warn_8),int(warn_9)))
       f.close()

def check_alert_record(current_time,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,file):
       send_alert = False
       f = open(directory+str(file)+'_alert_record.txt','r')
     
       record = f.read().splitlines()[0]
       f.close()      
       time_of_last_email_alert = datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]),int(record[11:13]),int(record[14:16]),int(record[17:19]),int(record[20:25]))
       previous_alerts_array =[bool(int(record[27])),bool(int(record[28])),bool(int(record[29])),bool(int(record[30])),bool(int(record[31])),bool(int(record[32])),bool(int(record[33])),bool(int(record[34])),bool(int(record[35]))]
       current_alerts_array   =[warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final]
       if datetime.datetime.now() > time_of_last_email_alert + datetime.timedelta(hours = 12) or previous_alerts_array != current_alerts_array:
             
             send_alert=True
       

       return send_alert    

   
def ch0_ch1_comparison(last_temp_ch0,last_temp_ch1,ethanol_bound):
        ethanol_alert=False
        if last_temp_ch1-last_temp_ch0 < ethanol_bound:
            ethanol_alert = True
    
        return ethanol_alert

def med_log_ticker(log_file,variable):

 f = open(log_file,'r')
 lines = f.read().splitlines()
 counter = float(lines[0])
 if counter>50:  
   if variable=='FRAr':
     f.close()
     f = open(log_file,'w')
     f.write(str(0))
     f.close()
   add_new_value=True
 else:
    if variable=='FRAr':
       f.close()
       f = open(log_file,'w')
       f.write(str(counter+1))
       f.close()
    add_new_value=False

 return add_new_value

def write_rolling_files(f_short,short_log_file,f_med,med_log_file,current_time,current_value,variable):

        clear_file(short_log_file)
        f_short.write("{} -- {}\n".format(current_time, current_value))
       
        if med_log_ticker('/home/supernemo/TemperatureLogs/New Logger Files/log_counter.txt',variable)==True:
          clear_file(med_log_file)             
          f_med.write("{} -- {}\n".format(current_time, current_value,variable))

def write_file(variable_settings,variable,chiller_status):
    log_file ,short_log_file,med_log_file = path(variable)

    f = open(log_file,'a')
    f_short = open(short_log_file,'a')
    f_med = open(med_log_file, 'a')
    trigger_short_term_average,trigger_med_term_average,trigger_bound,current_time,current_value,chiller_off_alert,last_log_time,last_short_log_time,last_short_log_value = compare_rolling_averages_to_current_value(variable_settings,variable,chiller_status)
    automated_log_time = automated_logger_time()
    write_rolling_files(f_short,short_log_file,f_med,med_log_file,current_time,current_value,variable) 

    if trigger_short_term_average == 'yes' or trigger_med_term_average == 'yes' or trigger_bound =='yes' or automated_log_time==True or chiller_off_alert =='yes':
        if current_time>last_log_time + datetime.timedelta(minutes=4) or chiller_off_alert == 'yes':

           f.write("{} -- {}\n".format(last_short_log_time,last_short_log_value))
           f.write("{} -- {}\n".format(current_time,current_value))
           print(variable + ' changed,logged in ' + log_file+str('\n----------------------------------'))

        else:
           print(variable + ' checked, change not logged due to previous log being under 4 minutes ago'+str('\n----------------------------------'))

    else:
           print(variable + ' checked, change not logged'+str('\n----------------------------------'))

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
end_time = datetime.datetime.now()
start_time=end_time-datetime.timedelta(days=2)
current_time = datetime.datetime.now()
write_alert_record(current_time,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,'current')
if activate_alert_final == True or ethanol_alert_final:
    if check_alert_record(current_time,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,'previous') == True:
          print('\nSending Alert Email...')
          email_alert(True,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,start_time,end_time,'stored')
          write_alert_record(current_time,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,'previous')
    else:
          print('No Email Alert Sent due to having sent an alert with the same warnings under 12 hours ago')

elif automated_email_time() ==True:
    print('\nSending daily update email...')
    email_alert(True,warn_sense_final,warn_0_final,warn_1_final,warn_2_final,warn_p_final,warn_FRHe_final,warn_FRAr_final,ethanol_alert_final,chiller_off_alert_final,start_time,end_time,'stored')

else:
    print('No Email Alert Sent')

