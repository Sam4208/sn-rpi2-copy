import datetime
from datetime import timedelta
from matplotlib.dates import  DateFormatter
import matplotlib.pyplot as plt
import smtplib
import imghdr
from email.message import EmailMessage
import ClientHistoryReadout as chis
import numpy as np

"""
year = 2021
year2 = 2021

month=11
month2=11

day=8
day2 = 9

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

def plot_temp_data_email(input_file,fig,ax,title):


    
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    precision = 1
    
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
            
        
    
    
    ax.set_title(title)
    ax.plot_date(time,temp,'b-',linewidth=1)
    fig.autofmt_xdate()
    ax.set_ylim([min(temp),max(temp)*1.1])
    ax.set_xlim([datetime.datetime(year, month, day,hour,min_,second,milisecond), datetime.datetime(year2, month2, day2,hour2,min_2,second,milisecond2)])
    






def save_plot_emergency_email():
    directory='/home/supernemo/TemperatureLogs/New Logger Files/'
    fig, ((ax0,ax1, ax2, ax3,ax4)) = plt.subplots(5, 1,figsize=(10, 17), dpi=80)
    fig.subplots_adjust(hspace=0.1)     
    #/temporarytest/
    plot_temp_data_email(str(directory)+'SensorTemp.txt',fig,ax0,'SensorTemp')
    plot_temp_data_email(str(directory)+'Temp_Ch0.txt',fig,ax1,'FGT1')
    plot_temp_data_email(str(directory)+'Temp_Ch1.txt',fig,ax2,'FGT0')
    plot_temp_data_email(str(directory)+'Temp_Ch2.txt',fig,ax3,'BPT2')
    plot_temp_data_email(str(directory)+'Pressure.txt',fig,ax4,'Pressure')

    fig.savefig('/home/supernemo/SVN/trunk/source/scripts/emergency_plots/plot_save.png')   # save the figure to file
    plt.close(fig)
   


def email_alert(plot,warn_sense,warn_0,warn_1,warn_2,warn_3,warn_4):

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
            email_text = list_email_info[line]
        elif line> 8:
            recipient_address.append(list_email_info[line])
       
    f.close()
    
    
    newMessage = EmailMessage()                         
    newMessage['Subject'] = email_subject
    newMessage['From'] = gmail_user                 
    newMessage['To'] = recipient_address                
    newMessage.set_content(email_text) 

    if plot == True:

        save_plot_emergency_email()
    
    
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
         
