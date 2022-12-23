"""
created by spratt 6/12/22
A series of functions used by the GUI allowing the read in of temporary storage files to get data for all variables
"""
import datetime
from datetime import timedelta
from matplotlib.dates import  DateFormatter
import subprocess
import matplotlib.pyplot as plt
import smtplib
import imghdr
from email.message import EmailMessage
import numpy as np
import matplotlib.dates as mdates
log_dir ='/home/supernemo/TemperatureLogs/New Logger Files/'

string1=30
string2=36
now=str(datetime.datetime.now())

def get_last_value_time_from_log(input_file):

        with open(input_file) as f:
            last_line = f.readlines()[-1]
        f.close()

        value = (last_line[string1:string2])
        time = datetime.datetime(int(last_line[0:4]),int(last_line[5:7]),int(last_line[8:10]),int(last_line[11:13]),int(last_line[14:16]),int(last_line[17:19]),int(last_line[20:25]))
        if value =='2022-11-29 12:36:53.209280 -- Chiller off'[string1:string2]:
            value='Chiller off'
        else:
          try:
              
              value = float(value)

          except ValueError:
              pass

        return time,value

def find_time_GUI_turned_on(input_file):
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    

    for i in range(0,int(len(lines))):
         if lines[i][28:29]=='\'':
              
              time_GUI_on = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25]))
              break
         
    return time_GUI_on    

def get_value_time_from_log(input_file,datetime_start,datetime_end):
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    
    for i in range(0,int(len(lines))):
        
        temp_add = (lines[i][string1:string2])
        if temp_add =='2022-11-29 12:36:53.209280 -- Chiller off'[string1:string2]:
            continue
        else:

          try:
              float(temp_add)
              time_add = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25]))
              temp_add = float(temp_add)
              if time_add > datetime_start and time_add < datetime_end:
            
               
                  time = np.append(time,time_add)
                  temp = np.append(temp,temp_add)
          
          except ValueError:
          
              pass              
              
    return time,temp    


def set_tick_frequency(ax,start_time,end_time,font_size):

    
     delt_hour=end_time.hour-start_time.hour
     delt_day=end_time.day-start_time.day
     delt_month=end_time.month-start_time.month
     delt_year=end_time.year-start_time.year
     delt_hours = delt_hour
     delt_hours +=delt_year*365.25*24
     delt_hours +=delt_month*30*24
     delt_hours +=delt_day*24


     if delt_hours<3:
           
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        date_format ="%m/%d-%H:%M" 
        x_axis_label='Time (month/day-hour:minute)'
        linewidth_adjustment=0
     elif delt_hours<10:
        
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
        date_format ="%m/%d-%H:%M" 
        x_axis_label='Time (month/day-hour:minute)'
        linewidth_adjustment=0
     elif delt_hours<50:
    
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=5))
        date_format ="%m/%d-%H" 
        x_axis_label='Time (month/day-hour)'
        linewidth_adjustment=0
     elif delt_hours<240:# between 2 day and 10 days
    
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        date_format ="%Y/%m/%d" 
        x_axis_label='Time (Year/month/day)'
        linewidth_adjustment=0.3
    
     elif delt_hours<1000:# between 1 day and 10 days
        linewidth_adjustment=0.3
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        date_format ="%Y/%m/%d" 
        x_axis_label='Time (Year/month/day)'    
        
     elif delt_hours<5000:# between 1 day and 10 days
        linewidth_adjustment=0.3
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        date_format ="%Y/%m/%d" 
        x_axis_label='Time (Year/month/day)'       
    
     elif delt_hours<10000:# between 1 day and 10 days
        linewidth_adjustment=0.3
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        date_format ="%Y/%m/%d" 
        x_axis_label='Time (Year/month/day)'   
    
     elif delt_hours>10000:# between 1 day and 10 days
        linewidth_adjustment=0.3
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=8))
        date_format ="%Y/%m/%d" 
        x_axis_label='Time (Year/month/day)'  
         
     ax.xaxis.set_major_formatter(DateFormatter(date_format)) 
     ax.set_xlabel(x_axis_label,fontsize=font_size)
     return linewidth_adjustment

def plot_all_variables_sub_function(ax,chiller_stat,chiller_off_alert,start_time,end_time,a1,a2,a3,a4,log_file):
    if log_file =='GUI':
       directory=log_dir+'GUI_temporary_logs/'
       log_file_type = 'GUI_log.txt'
       time_GUI_on = find_time_GUI_turned_on(str(directory)+'FGT1'+log_file_type)
    else:
       log_file_type ='.txt'
       time_GUI_on=''
       directory = log_dir       

    line_width_standard = 0.6
    font_size=4
    ax.clear()
    for label in ax.xaxis.get_ticklabels():
        label.set_fontsize(font_size)
        label.set_rotation(30)    

    for label in ax.yaxis.get_ticklabels():
        label.set_fontsize(font_size)

    linewidth_adjustment = set_tick_frequency(ax,start_time,end_time,font_size)
    
    if ax == a1:
         times,values = get_value_time_from_log(str(directory)+'Pressure'+log_file_type,start_time,end_time)
         upper_bound = 0.01
         lower_bound = 0.01
         title = 'Primary Bubbler Pressure'
         y_label = 'Pressure (bar)'
         minimum  = min(values)
         maximum  = max(values)
         ax.plot_date(times, values, '-',linewidth=line_width_standard-linewidth_adjustment)
         if log_file =='GUI':
             ax.axvline(time_GUI_on,color='black',linewidth=0.3)
    if ax == a4:
         times,values = get_value_time_from_log(str(directory)+'BPT'+log_file_type,start_time,end_time)
         upper_bound = 0.01
         lower_bound = 0.01
         title ='Primary Bubbler Temperature'
         y_label = 'Temperature (C)'
         line_format = '-'
         line_width = 1-linewidth_adjustment
         minimum = min(values)
         maximum = max(values)
         label = 'Temperature'
         ax.plot_date(times, values, '-',linewidth=line_width_standard-linewidth_adjustment)
         if log_file =='GUI':
             ax.axvline(time_GUI_on,color='black',linewidth=0.3)
    if ax == a2:
       times_FGT1,values_FGT1 = get_value_time_from_log(str(directory)+'FGT1'+log_file_type,start_time,end_time)
       times_FGT2,values_FGT2 = get_value_time_from_log(str(directory)+'FGT2'+log_file_type,start_time,end_time)
       times_WB,values_WB = get_value_time_from_log(str(directory)+'Water_Bath'+log_file_type,start_time,end_time)
       upper_bound =0.0025
       lower_bound = 0.0025
       title = 'Secondary Bubbler Temperatures'
       y_label = 'Temperature (C)'
       ax.plot_date(times_FGT1, values_FGT1, 'g-', label="FG T1(bot)",linewidth=line_width_standard+0.2-linewidth_adjustment)
       ax.plot_date(times_FGT2, values_FGT2, 'r-', label="FG T2(top)",linewidth=line_width_standard+0.1-linewidth_adjustment)
       if log_file =='GUI':
             ax.axvline(time_GUI_on,color='black',linewidth=0.3)
       if chiller_stat=='on' or chiller_off_alert==True:
              ax.plot_date(times_WB, values_WB, 'b-', label="Water Bath",linewidth=line_width_standard-0.1-linewidth_adjustment)
              ax.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=3, borderaxespad=0, prop={'size':4})
              minimum = min(min(values_FGT1),min(values_FGT2),min(values_WB))
              maximum = max(max(values_FGT1),max(values_FGT2),min(values_WB))
       if  chiller_stat=='off' and chiller_off_alert ==False:
              ax.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0, prop={'size':4}) 
              minimum = min(min(values_FGT1),min(values_FGT2))
              maximum = max(max(values_FGT2),max(values_FGT2))
    if ax == a3: 
           title = 'Flowrate of He and Ar'
           y_label = 'Flow rate (l/min)'
           upper_bound = 0.05
           lower_bound = 0.05
           times_FRHe,values_FRHe = get_value_time_from_log(str(directory)+'FRHe'+log_file_type,start_time,end_time)
           times_FRAr,values_FRAr = get_value_time_from_log(str(directory)+'FRAr'+log_file_type,start_time,end_time)
           ax.plot_date(times_FRHe, values_FRHe, 'r-', label="Helium",linewidth=line_width_standard+0.2-linewidth_adjustment)
           ax.plot_date(times_FRAr, values_FRAr, 'b-', label="Argon x 100",linewidth=line_width_standard+0.1-linewidth_adjustment)
           ax.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0, prop={'size':4})
           minimum = min(min(values_FRHe),min(values_FRAr))
           maximum = max(max(values_FRHe),max(values_FRAr))
           if log_file =='GUI':
              ax.axvline(time_GUI_on,color='black',linewidth=0.3)
              
    min_ = minimum-(np.sqrt(maximum**2)*lower_bound)
    max_ = maximum+(np.sqrt(maximum**2)*upper_bound)
    ax.set_title(title+'\n',fontsize=font_size+1)
    ax.set_ylabel(y_label,fontsize=font_size)   
    ax.set_ylim(min_, max_)
    
    
       
def plot_all_variables(f,chiller_stat,chiller_off_alert,time_start,time_end,log_file_type):    
    
    a1 = plt.subplot(2,2,1)
    a2 = plt.subplot(2,2,2)
    a3 = plt.subplot(2,2,3)
    a4 = plt.subplot(2,2,4)
    
    axis = [a1,a2,a3,a4]
    maximum,minimum = -100,+100
    for i in range(0,4):
  
        plot_all_variables_sub_function(axis[i],chiller_stat,chiller_off_alert,time_start,time_end,a1,a2,a3,a4,log_file_type)

    a1.set_xlim(time_start+datetime.timedelta(hours=2),time_end+datetime.timedelta(minutes=2))
    a2.set_xlim(time_start+datetime.timedelta(hours=2),time_end+datetime.timedelta(minutes=2))
    a3.set_xlim(time_start+datetime.timedelta(hours=2),time_end+datetime.timedelta(minutes=2))
    a4.set_xlim(time_start+datetime.timedelta(hours=2),time_end+datetime.timedelta(minutes=2))
   
    f.subplots_adjust(bottom=0.12, wspace=0.19, hspace=0.43)
    return f
   
def chiller_status():
              variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/HaakeValues.py','T'], check=True, capture_output=True, text=True).stdout
              if float(variable_output) ==float(999):
                  chiller_stat='off'
              else:
                  chiller_stat='on'

              return chiller_stat

def alert_text_set(email_text_alert,email_text_normal,warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert,chiller_stat):

    if warn_sens ==True:
        email_text_alert+='Water Bath temperature outside set bound\n'
    if warn_FGT1 ==True:
        email_text_alert+='FGT1 value outside set bound\n'
    if warn_FGT2 ==True:
        email_text_alert+='FGT2 value outside set bound\n'
    if warn_BPT ==True:
        email_text_alert+='BPT value outside set bound\n'
    if warn_pres ==True:
        email_text_alert+='Bubbler pressure value outside set bound\n'
    if warn_FRHe ==True:
        email_text_alert+='Helium Flow Rate value outside set bound\n'
    if warn_FRAr ==True:
        email_text_alert+='Argon Flow Rate value outside set bound\n'
    if warn_ethanol ==True:
        email_text_alert+='Ethanol level warning - FGT1 and FGT2 have  exceeded relative bound\n'
    if chiller_off_alert ==True:
        email_text_alert+='The Water Bath has been turned off recently\n'
        email_text_normal+='\n\nNotifications:\n\nThe Water Bath has been turned off recently\n'
    if chiller_stat == 'off' and chiller_off_alert ==False:
              email_text_alert+='The Water Bath is still off\n'
              email_text_normal+='\n\nNotifications:\n\nThe Water Bath is still off\n\n'


    if sum([warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_ethanol,warn_FRHe,warn_FRAr])==0:
        email_text=email_text_normal
    else:
         email_text = email_text_alert
    return email_text

def email_alert(plot,warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert,time_start,time_end,email):
    chiller_stat = chiller_status()
    recipient_address=[]

    f = open("/home/supernemo/SVN/trunk/source/scripts/email_alert_settings.txt", "r")
    list_email_info = f.read().splitlines()

    for line in range (0,len((list_email_info))):

        if line == 1:
            gmail_user  = list_email_info[line]
        elif line == 3:
            gmail_password = list_email_info[line]
        elif line== 5:
            email_subject= list_email_info[line]
        elif line== 7:
            email_text_alert = list_email_info[line]+'\n\nAlerts:\n\n'
        elif line==9:
            email_text_normal = list_email_info[line]
        elif line> 10:
            recipient_address.append(list_email_info[line])

    f.close()

    email_text =  alert_text_set(email_text_alert,email_text_normal,warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert,chiller_stat)

    if email =='stored':
          pass
    else:
          recipient_address =[email]

    newMessage = EmailMessage()
    newMessage['Subject'] = email_subject
    newMessage['From'] = gmail_user
    newMessage['To'] = recipient_address
    newMessage.set_content(email_text)

    if plot == True:
        f = plt.figure(dpi=170) 
        f= plot_all_variables(f,chiller_stat,chiller_off_alert,time_start,time_end,'full')
        f.savefig('/home/supernemo/SVN/trunk/source/scripts/emergency_plots/plot_save.png')   # save the figure to file
        plt.close(f)

    with open('/home/supernemo/SVN/trunk/source/scripts/emergency_plots/plot_save.png', 'rb') as p:
       image_data = p.read()
       image_type = imghdr.what(p.name)
       image_name = p.name
    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    try:

        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        smtp_server.ehlo()

        smtp_server.login(gmail_user, gmail_password)

        smtp_server.send_message(newMessage)

        smtp_server.close()

        print ("Email sent successfully!")

    except Exception as ex:

        print ("Something went wrong….",ex)


def variable_status(variable):
 while True:
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
        continue
    break

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
 
              if time_add > datetime.datetime.now()-datetime.timedelta(hours=5) and lines[i][30:38] !='2022-11-29 12:36:53.209280 -- Chiller off'[30:38] :
                  f_2.write(lines[i])
 
    f_2.close()

   
   

def write_data_temporary_log(variable):

        lines = read_in_file(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','r')
        last_line = lines[len(lines)-1]
        time_last_datapoint = datetime.datetime(int(last_line[0:4]),int(last_line[5:7]),int(last_line[8:10]),int(last_line[11:13]),int(last_line[14:16]),int(last_line[17:19]),int(last_line[20:25]))
        if time_last_datapoint+datetime.timedelta(minutes=1) < datetime.datetime.now():
           current_value = variable_status(variable)

           with open(log_dir+'GUI_temporary_logs/'+str(variable)+'GUI_log.txt','a') as f:
                  f.write("{} '' {}\n".format(datetime.datetime.now(),current_value))
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


def check_current_alerts():
       send_alert = False
       f = open(log_dir+'current_alert_record.txt','r')
     
       record = f.read().splitlines()[0]
       f.close()      
       current_alerts_array =[bool(int(record[27])),bool(int(record[28])),bool(int(record[29])),bool(int(record[30])),bool(int(record[31])),bool(int(record[32])),bool(int(record[33])),bool(int(record[34])),bool(int(record[35]))]       
       [warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert] = current_alerts_array
       alert_text =  alert_text_set('','GOOD',warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert,'on')
       return alert_text


def clean_GUI_log(log_file):
    with open(log_file,'r') as f:
        line_number = 1
        lines=f.readlines()
    
        with open(log_file,'w') as f_2:
        

            for i in range(0,len(lines)):
                   
               if  datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25])) > datetime.datetime.now()-datetime.timedelta(hours=5) :   
                    f_2.write(lines[i])
                   
               else:
                  print(lines[i])
    f_2.close()
    f.close()
