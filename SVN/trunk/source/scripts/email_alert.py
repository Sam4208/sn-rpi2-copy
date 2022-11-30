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
"""
year = 2022
year2 = 2022

month=11
month2=11

day=10
day2 = 13

hour=15
hour2=16

min_=0
min_2=0

second=0
second2=0

milisecond=0
milisecond2=0
"""

now=str(datetime.datetime.now())

year = int(now[0:4])
year2 = int(now[0:4])

month=int(now[5:7])
month2=int(now[5:7])

day=int(now[8:10])-1
day2 = int(now[8:10])

hour=int(now[11:13])
hour2=int(now[11:13])

min_=int(now[14:16])
min_2=int(now[14:16])

second=int(now[17:19])
second2=int(now[17:19])

milisecond=int(now[20:25])
milisecond2=int(now[20:25])

def plot_temp_data_email(input_file,title):


    
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    precision = 1
    
    no_events = int(len(lines)/precision)
    
    for i in range(0,no_events):
        i = i* precision
        temp_add = (lines[i][30:38])
        if temp_add =='2022-11-29 12:36:53.209280 -- Chiller off'[30:38]:
            continue
        else:

#        print(temp_add)
          try:
              float(temp_add)
              time_add = datetime.datetime(int(lines[i][0:4]),int(lines[i][5:7]),int(lines[i][8:10]),int(lines[i][11:13]),int(lines[i][14:16]),int(lines[i][17:19]),int(lines[i][20:27]))
#              print(time_add)  
              temp_add = float(temp_add)
             # print(time_add,datetime.datetime(year, month, day,hour,min_,second,milisecond))
              if time_add > datetime.datetime(year,month,day,hour,min_,second,milisecond) and time_add<datetime.datetime(year2,month2,day2,hour2,min_2,second2,milisecond2):
            
               
                  time = np.append(time,time_add)
                  temp = np.append(temp,temp_add)
            
          except ValueError:
             # continue
              print('error reading log file - data point not read in - temp: '+str(temp_add)+'   time:'+str(time_add))
            
        
    
    """
    ax.set_title(title)
    ax.plot_date(time,temp,'b-',linewidth=1)
    fig.autofmt_xdate()
    ax.set_ylim([min(temp),max(temp)*1.1])
    ax.set_xlim([datetime.datetime(year, month, day,hour,min_,second,milisecond), datetime.datetime(year2, month2, day2,hour2,min_2,second,milisecond2)])
    """

    return time,temp    



def plot_data(subplot, fig, variable,x,y,date_format,font_size):
    # Function to take in the data and plot the graph
    
    #print(x)
    #print(y)
   # subplot.clear()
   # subplot.get_xaxis().get_major_formatter().set_useOffset(False)
   # for label in subplot.xaxis.get_ticklabels():
   #     label.set_rotation(30)
   # fig.subplots_adjust(left=0.16, bottom=0.35, right=0.90, top=0.90, wspace=0.2, hspace=0)
   #subplot.set_xlabel(setText("12"))
    
    minimum = min(y)
    maximum = max(y)
    
    
    if variable == "Pressure":
        minimum = minimum-(np.sqrt(minimum**2)*0.08)
        maximum = maximum+(np.sqrt(minimum**2)*0.08)
        subplot.set_title('Primary Bubbler Pressure'+'\n',fontsize=font_size+1)
        subplot.set_ylabel('Pressure (bar)',fontsize=font_size)
    elif variable == "Temp_Ch2":
        minimum = minimum-(np.sqrt(maximum**2)*0.0025)
        maximum = maximum+(np.sqrt(maximum**2)*0.0025)
        subplot.set_title("Primary Bubbler Temperature"+'\n',fontsize=font_size+1)
        subplot.set_ylabel("Temperature (C)",fontsize=font_size)

    if min(y,default = "EMPTY" ) < minimum:
        minimum = (min(y))*0.925

    if max(y,default = "EMPTY") > maximum:
        maximum = (max(y))*1.075
    
    subplot.set_ylim(minimum, maximum)
    subplot.plot_date(x, y, '-',linewidth=1)   




def save_plot_emergency_email(chiller_stat,chiller_off_alert):

    
    directory='/home/supernemo/TemperatureLogs/New Logger Files/'

    #fig, ((ax0,ax1, ax2, ax3,ax4)) = plt.subplots(5, 1,figsize=(10, 17), dpi=80)


   # fig.subplots_adjust(hspace=0.1)

    bath_time,bath_temp  = plot_temp_data_email(str(directory)+'Water_Bath.txt','Water Bath')

    FGT1_time,FGT1_temp  = plot_temp_data_email(str(directory)+'FGT1.txt','FGT1')

    FGT2_time,FGT2_temp  = plot_temp_data_email(str(directory)+'FGT2.txt','FGT2')

    BPT_time,BPT_temp    = plot_temp_data_email(str(directory)+'BPT.txt','BPT')
   
    pres_time, pres_temp = plot_temp_data_email(str(directory)+'Pressure.txt','Pressure')

    FRHe_time, FRHe_temp = plot_temp_data_email(str(directory)+'FRHe.txt','FRHe')

    FRAr_time, FRAr_temp = plot_temp_data_email(str(directory)+'FRAr.txt','FRAr')

    
    f = plt.figure(dpi=170) 

    date_format ="%m/%d-%H"
    a1 = plt.subplot(2,2,1)
    a2 = plt.subplot(2,2,2)
    a3 = plt.subplot(2,2,3)
    a4 = plt.subplot(2,2,4)

    x, y = FGT1_time,FGT1_temp
    x1,y1 = FGT2_time,FGT2_temp
    x2,y2 =BPT_time,BPT_temp
    x10, y10 = bath_time,bath_temp


    x3,y3 =  FRHe_time,FRHe_temp
    x4,y4 = FRAr_time,FRAr_temp
    y4_mult = [i/100 for i in y4]
# orginally y4_mult = [i*10 for i in y4] I believe this is wrong

    a1.clear()
    a2.clear()
    a3.clear()
    a4.clear()

    font_size=4
    
    for label in a1.xaxis.get_ticklabels():
        label.set_rotation(30)
        label.set_fontsize(font_size)
    for label in a2.xaxis.get_ticklabels():
        label.set_rotation(30)
        label.set_fontsize(font_size)
    for label in a3.xaxis.get_ticklabels():
        label.set_fontsize(font_size)
        label.set_rotation(30)
    for label in a4.xaxis.get_ticklabels():
        label.set_fontsize(font_size)
        label.set_rotation(30)    

    for label in a4.yaxis.get_ticklabels():
        label.set_fontsize(font_size)
    for label in a3.yaxis.get_ticklabels():
        label.set_fontsize(font_size)
    for label in a2.yaxis.get_ticklabels():
        label.set_fontsize(font_size)
    for label in a1.yaxis.get_ticklabels():
        label.set_fontsize(font_size)
    
    
    a1.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    a2.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    a3.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    a4.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    a1.xaxis.set_major_formatter(DateFormatter(date_format))
    a2.xaxis.set_major_formatter(DateFormatter(date_format))   
    a3.xaxis.set_major_formatter(DateFormatter(date_format))
    a4.xaxis.set_major_formatter(DateFormatter(date_format))
                  
    x_axis_label = 'Time (month/day-hour)'   

    a4.set_xlabel(x_axis_label,fontsize=font_size)
    a3.set_xlabel(x_axis_label,fontsize=font_size)  
    a2.set_xlabel(x_axis_label,fontsize=font_size)
    a1.set_xlabel(x_axis_label,fontsize=font_size)

    plot_data(a1, f, "Pressure",pres_time,pres_temp,date_format,font_size)


  





# This is repeated, maybe have function to set all labels at start
    label_ch0 = 'FGT1'
    label_ch1 = 'FGT2'
    label_ch2 = 'BPT'
    
    a2.plot_date(x, y, 'g-', label="FG T0 (bot)",linewidth=1.2)
    a2.plot_date(x1, y1, 'r-', label="FG T1 (top)",linewidth=1.1)
    if chiller_stat=='on' or chiller_off_alert==True:
       a2.plot_date(x10, y10, 'b-',label="Water Bath",linewidth=0.9)
       a2.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
          ncol=3, borderaxespad=0, prop={'size':4})
       
       minimum2 = min(min(y),min(y1),min(y10))-2
       maximum2 = max(max(y),max(y1),max(y10))+2
    else:
       
       a2.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
          ncol=2, borderaxespad=0, prop={'size':4})   
       minimum2 = min(min(y),min(y1))
       maximum2 = max(max(y),max(y1))

    a2.set_ylim(minimum2-(np.sqrt(maximum2**2)*0.003), maximum2+(np.sqrt(maximum2**2)*0.003))
    a2.set_title('Secondary Bubbler Temperatures'+'\n',fontsize=font_size+1 )
    a2.set_ylabel('Temperature (C)',fontsize=font_size)
        
            

    
    

    a3.plot_date(x3, y3, 'b-', label='Helium',linewidth=1.2)
    a3.plot_date(x4, y4_mult, 'r-', label='Argon x 100',linewidth=1)
    a3.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
          ncol=2, borderaxespad=0, prop={'size':4})


    minimum3 = min(min(y3),min(y4_mult))
    maximum3 = max(max(y3),max(y4_mult))
    maximum3=maximum3+0.1*maximum3  
    minimum3=minimum3-0.1*maximum3             
    a3.set_ylim(minimum3, maximum3)
    a3.set_title('Flowrate of He and Ar'+'\n',fontsize=font_size+1)
    a3.set_ylabel('Flow rate (l/min)',fontsize=font_size ) 


    plot_data(a4, f,"Temp_Ch2",BPT_time,BPT_temp,date_format,font_size)

#    f.subplots_adjust(left=0.0, bottom=0, right=0, top=0, wspace=0.5, hspace=0.6)
    f.subplots_adjust(bottom=0.12, wspace=0.19, hspace=0.43)

    """
    if warn_ethanol==True:
         fig2, ((ax0,ax1)) = plt.subplots(number_of_axis, 1,figsize=(10, 17), dpi=80)
         fig2.subplots_adjust(hspace=0.1)     
         plot_temp_data_email(str(directory)+'Temp_Ch0.txt',fig2,ax0,'FGT1')
         plot_temp_data_email(str(directory)+'Temp_Ch1.txt',fig2,ax1,'FGT2')
         fig = fig2
   
    """
    f.savefig('/home/supernemo/SVN/trunk/source/scripts/emergency_plots/plot_save.png')   # save the figure to file
    plt.close(f)
   
def chiller_status():
              variable_output = subprocess.run(['/home/supernemo/SVN/trunk/source/scripts/HaakeValues.py','T'], check=True, capture_output=True, text=True).stdout
              if float(variable_output) ==float(999):
                  chiller_stat='off'
              else:
                  chiller_stat='on'
            
              return chiller_stat
 
def email_alert(plot,warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_FRHe,warn_FRAr,warn_ethanol,chiller_off_alert):
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
    
    if warn_sens ==True:
        email_text_alert+='Water Bath temperature outside set bound\n\n'
    if warn_FGT1 ==True:
        email_text_alert+='FGT1 value outside set bound\n\n'
    if warn_FGT2 ==True:
        email_text_alert+='FGT2 value outside set bound\n\n'
    if warn_BPT ==True:
        email_text_alert+='BPT value outside set bound\n\n'
    if warn_pres ==True:
        email_text_alert+='Bubbler pressure value outside set bound\n\n'
    if warn_FRHe ==True:
        email_text_alert+='Helium Flow Rate value outside set bound\n\n'
    if warn_FRAr ==True:
        email_text_alert+='Argon Flow Rate value outside set bound\n\n'
    if warn_ethanol ==True:
        email_text_alert+='Ethanol level warning - FGT1 and FGT2 have  exceeded relative bound\n\n'
    if chiller_off_alert ==True:
        email_text_alert+='The Water Bath has been turned off recently\n\n'
        email_text_normal+='\n\nNotifications:\n\nThe Water Bath has been turned off recently\n\n'   
    if chiller_stat == 'off' and chiller_off_alert ==False:
              email_text_alert+='The Water Bath is still off\n\n'
              email_text_normal+='\n\nNotifications:\n\nThe Water Bath is still off\n\n' 

    if sum([warn_sens,warn_FGT1,warn_FGT2,warn_BPT,warn_pres,warn_ethanol,warn_FRHe,warn_FRAr])==0:
        email_text=email_text_normal
    else:
         email_text = email_text_alert


    newMessage = EmailMessage()                         
    newMessage['Subject'] = email_subject
    newMessage['From'] = gmail_user                 
    newMessage['To'] = recipient_address                
    newMessage.set_content(email_text) 

    if plot == True:
    
        save_plot_emergency_email(chiller_stat,chiller_off_alert)
    
    
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
         

#email_alert(True,False,False,False,False,False,False)
