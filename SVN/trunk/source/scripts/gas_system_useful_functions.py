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

def plot_temp_data_email(input_file,title,datetime_start,datetime_end):

    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    precision = 1
    
    no_events = int(len(lines)/precision)
    
    for i in range(0,no_events):
        i = i* precision
        temp_add = (lines[i][string1:string2])
        if temp_add =='2022-11-29 12:36:53.209280 -- Chiller off'[string1:string2]:
            continue
        else:

#        print(temp_add)
          try:
              float(temp_add)
              time_add = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:25]))
#              print(time_add)  
              temp_add = float(temp_add)
             # print(time_add,datetime.datetime(year, month, day,hour,min_,second,milisecond))
              if time_add > datetime_start and time_add < datetime_end:
            
               
                  time = np.append(time,time_add)
                  temp = np.append(temp,temp_add)
          
          except ValueError:
          
             
              
              print('error reading log file - data point not read in - temp: '+str(temp_add)+'   time:'+str(time_add))
              
       
    
    """
    ax.set_title(title)
    ax.plot_date(time,temp,'b-',linewidth=1)
    fig.autofmt_xdate()
    ax.set_ylim([min(temp),max(temp)*1.1])
    ax.set_xlim([datetime.datetime(year, month, day,hour,min_,second,milisecond), datetime.datetime(year2, month2, day2,hour2,min_2,second,milisecond2)])
    """

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
        
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
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

def plot_all_variables_sub_function(ax,chiller_stat,chiller_off_alert,start_time,end_time,directory,a1,a2,a3,a4):
    
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
         times,values = plot_temp_data_email(str(directory)+'Pressure.txt','Pressure',start_time,end_time)
         upper_bound = 0.01
         lower_bound = 0.01
         title = 'Primary Bubbler Pressure'
         y_label = 'Pressure (bar)'
         minimum  = min(values)
         maximum  = max(values)
         ax.plot_date(times, values, '-',linewidth=line_width_standard-linewidth_adjustment)
    if ax == a4:
         times,values = plot_temp_data_email(str(directory)+'BPT.txt','BPT',start_time,end_time)
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
    if ax == a2:
       times_FGT1,values_FGT1 = plot_temp_data_email(str(directory)+'FGT1.txt','FGT1',start_time,end_time)
       times_FGT2,values_FGT2 = plot_temp_data_email(str(directory)+'FGT2.txt','FGT2',start_time,end_time)
       times_WB,values_WB = plot_temp_data_email(str(directory)+'Water_Bath.txt','Water_Bath',start_time,end_time)
       upper_bound =0.0025
       lower_bound = 0.0025
       title = 'Secondary Bubbler Temperatures'
       y_label = 'Temperature (C)'
       ax.plot_date(times_FGT1, values_FGT1, 'g-', label="FG T1(bot)",linewidth=line_width_standard+0.2-linewidth_adjustment)
       ax.plot_date(times_FGT2, values_FGT2, 'r-', label="FG T2(top)",linewidth=line_width_standard+0.1-linewidth_adjustment)
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
           times_FRHe,values_FRHe = plot_temp_data_email(str(directory)+'FRHe.txt','FRHe',start_time,end_time)
           times_FRAr,values_FRAr = plot_temp_data_email(str(directory)+'FRAr.txt','FRAr',start_time,end_time)
           ax.plot_date(times_FRHe, values_FRHe, 'r-', label="Helium",linewidth=line_width_standard+0.2-linewidth_adjustment)
           ax.plot_date(times_FRAr, values_FRAr, 'b-', label="Argon x 100",linewidth=line_width_standard+0.1-linewidth_adjustment)
           ax.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0, prop={'size':4})
           minimum = min(min(values_FRHe),min(values_FRAr))
           maximum = max(max(values_FRHe),max(values_FRAr))
           

    min_ = minimum-(np.sqrt(maximum**2)*lower_bound)
    max_ = maximum+(np.sqrt(maximum**2)*upper_bound)
    ax.set_title(title+'\n',fontsize=font_size+1)
    ax.set_ylabel(y_label,fontsize=font_size)   
    ax.set_ylim(min_, max_)
    print(min_,max_)
def plot_all_variables(chiller_stat,chiller_off_alert,time_start,time_end):    

    directory='/home/supernemo/TemperatureLogs/New Logger Files/'

    f = plt.figure(dpi=170) 
    
    a1 = plt.subplot(2,2,1)
    a2 = plt.subplot(2,2,2)
    a3 = plt.subplot(2,2,3)
    a4 = plt.subplot(2,2,4)

    axis = [a1,a2,a3,a4]
    maximum,minimum = -100,+100
    for i in range(0,4):
  
        plot_all_variables_sub_function(axis[i],chiller_stat,chiller_off_alert,time_start,time_end,directory,a1,a2,a3,a4)

    f.subplots_adjust(bottom=0.12, wspace=0.19, hspace=0.43)
    return f
   

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
    
    short_term_average_bound = variable_settings[0]
    medium_term_average_bound = variable_settings[1]
    if chiller_status=='off':
       upper_trigger = variable_settings[2]
       lower_trigger = variable_settings[3] 
    elif chiller_status=='on':
       upper_trigger = variable_settings[4]
       lower_trigger = variable_settings[5] 
    
    
    last_log_value,last_log_time = log_file_open(variable)
    current_time,current_value = get_current_datapoint(variable)
    
    trigger_short_term_average = 'no'
    trigger_med_term_average = 'no'   
    trigger_bound ='no'
    chiller_off_alert = 'no'

    if variable =='Water_Bath' and chiller_status=='off':  
       
       if (last_log_value) == '2022-11-29 12:36:53.209280 -- Chiller off'[30:38]:
             chiller_off_alert = 'no'
             
       else:
            chiller_off_alert = 'yes'
    else:

      trigger_short_term_average = compare_subfunction(current_value,'short',variable_settings,variable)
      trigger_med_term_average   = compare_subfunction(current_value,'med',variable_settings,variable)
      if current_value > upper_trigger or current_value < lower_trigger :

           trigger_bound ='yes'
  
    
      else:
            pass
    
    
    
  
    return trigger_short_term_average,trigger_med_term_average,trigger_bound,current_time,current_value,chiller_off_alert 

