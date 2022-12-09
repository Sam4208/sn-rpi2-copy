"""
created by spratt 6/12/22
A series of functions used by the GUI allowing the read in of temporary storage files to get data for all variables
"""

import numpy as np
import datetime
import subprocess

log_dir ='/home/supernemo/TemperatureLogs/New Logger Files/'



def variable_status(variable):

    try:


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

    except subprocess.CalledProcessError as e:
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print('CalledProcessError')
        variable_output = 'error'
    return float(variable_output)


def read_in_file(file,action):

    with open(file,action) as f:
        line_number = 1
        lines=f.readlines()
    f.close()     

    return lines

def create_temporary_GUI_log_file(variable):

    lines = read_in_file(log_dir+str(variable)+'.txt','r')
    
    with open(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','w') as f_2:


          for i in range(0,len(lines)):
#              print(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]))
              time_add = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25]))
 
              if time_add > datetime.datetime.now()-datetime.timedelta(hours=3) and lines[i][30:38] !='2022-11-29 12:36:53.209280 -- Chiller off'[30:38] :
                  f_2.write(lines[i])
 
    f_2.close()

   
   

def write_data_temporary_log(variable):

        lines =  read_in_file(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','r')
        last_line = lines[len(lines)-1]
        time_last_datapoint = datetime.datetime(int(last_line[0:4]),int(last_line[5:7]),int(last_line[8:10]),int(last_line[11:13]),int(last_line[14:16]),int(last_line[17:19]),int(last_line[20:25]))
        if time_last_datapoint+datetime.timedelta(minutes=1) < datetime.datetime.now():
           current_value = variable_status(variable)

           with open(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','a') as f:
                  f.write("{} -- {}         '\n".format(datetime.datetime.now(),current_value))
           f.close()


def get_data(variable):


       time=[]
       value=[]


       with open(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','r') as f:
          lines=f.readlines()
       f.close()

       for i in range(0,len(lines)):

             time_add = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25]))
             time=np.append(time,time_add)
             value=np.append(value,float(lines[i][30:36]))

       return time,value

