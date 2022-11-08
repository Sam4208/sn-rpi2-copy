import time
import datetime as dt
import sys
import re
import matplotlib.pyplot as plt
from matplotlib.dates import  DateFormatter
import numpy as np
import datetime as dt
"""
Elvis Penghui Li
script that generates temperature-time plot of historical data for all the sensors in gas system which includes FGT0, FGT1, BP temp, SensorTemp, takes input commands FG0,FG1,BP,sensor,
which would open the corrsponding file
the corrspondences are as shown:
FG0 = FG T0
FG1 = FG T1
BP = BP temp
sensor = sensorTemp

also take in the date which you want to start plot the graph, in format [YYYY-MM-DD] also the take in the time length which you want to be ploted, unit hours, in pure integer number form.

for the convinence of both see the long time trending and analysis the temperature change in detail, 3 different display modes are offered, take input command 'day','hour','minute'


the option "day" would plot a temperature-time graph with one data point per day, start from your choice of day.
the option "hour" would plot a temperature-time graph with one data point per hour, starting from 0:00 of your choice of day.
the option "minute" would plot a temperature-time graph with one data point per 4 minutes, starting from 0:00 of your choice of day.

There are 650 Temperature logs per day, around 25-27 per hour, counted twice by hand, used the data at 2016-11-18 as example.
ther script is generated based on this number count

enjoy using the script  ^-^
"""
temp = []
date = []

def which_file(file_input):
    file = str()
    if file_input == 'FG0':
        file = str("/home/supernemo/TemperatureLogs/Temp_Ch0.txt")
    elif file_input == 'FG1':
        file = str("/home/supernemo/TemperatureLogs/Temp_Ch1.txt")
    elif file_input == 'BP':
        file = str("/home/supernemo/TemperatureLogs/Temp_Ch2.txt")
    elif file_input == 'sensor':
        file = str("/home/supernemo/TemperatureLogs/SensorTemp.txt")
    else:
        print('This file does not exist.')
        quit()
    return file






def type_input(term):
    counts = 0
    if term == 'day':
        counts = 600
        
    elif term == 'hour':
        counts = 25
        
    elif term == 'minute':
        counts = 3
        
    else:
        print("That is not an option")
        quit()
    return counts

def search_date(date,file):
    string = date
    f = open(file,"r")
    flag = 0
    index = 0
    for line in f:
        index += 1
        if string in line:
            flag = 1
            break
    if flag == 0:
        print ('string',string,'not found')
        
    else:
        print ('string ',string,' found in line ', index)
        
    return index



def file_open(file,index,multiple,long_short):
    #print(index)
    f = open(file,'r')
    lines = f.readlines()
    for i in range (index,index+multiple*30,long_short):
        last_lines = lines[i]
        new_data_time = last_lines[11:27]
        
        new_data_time_2 = dt.datetime.strptime(new_data_time, "%Y-%m-%d %H:%M")
        
        new_data_temp = float(last_lines[47:53])
        temp.append(new_data_temp)
        date.append(new_data_time_2)
        
        """
        print(new_data_time)
        print(new_data_temp)
        print(temp)
        print(date)
        """
    return temp, date

def figure (x,y,kind,date,length,name):
    
        
        fig,ax = plt.subplots()
        #print(x)
        #print(y)
        ax.plot(x,y,clip_on=False,label=name)
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        interval_multples=True
        #print(kind)
        print(len(x))
        if len(x) >= 20:
            
            ax.xaxis.set_major_locator(plt.MaxNLocator(20))
        '''
        if kind == 3:
            if length/24 >= 1:
                n = length/60
                ax.xaxis.set_major_locator(plt.MaxNLocator(n))
        if kind == 25:
            if length/24 >= 3:
                n = length/24
                ax.xaxis.set_major_locator(plt.MaxNLocator(n))
        else:
            pass
        '''
        plt.yticks(fontsize = 6)
        plt.xticks(fontsize = 6 , rotation = -25)
        plt.xlabel('Date and Time (YYYY-MM-DD HH:MM)')
    
        plt.ylabel('Temperature (C)')
        plt.title('Temperature/Time (Historical data)')
        plt.suptitle('Plotting date is : ' + date + ' plot for : '+ str(length) + ' hours')
        plt.legend()
        ax.set_ylim(10,40)
    
        plt.show()
    
    
    
        
        
    





file_read = input('Which sensor temperature would you like to browse?[FG0/FG1/BP/sensorTemp] :')
file = which_file(file_read)
date_input = input('which day would you like to see (YYYY-MM-DD) :')
length_input = int(input ('How long would you see the plot for? (in integer hours) :'))
print('\nAs an expaination, the option "day" would plot a temperature-time graph with one data point per day, start from your choice of day. \nthe option "hour" would plot a temperature-time graph with one data point per hour, starting from 0:00 of your choice of day. \nthe option "minute" would plot a temperature-time graph with one data point per 4 minutes, starting from 0:00 of your choice of day.')
print('\nAs an precautiuon to a super massy x-axis, only 30 locators are allowed in the "hour" mode, so please be aware of that, also the MaxNLocator limit is NOT implemented on the "day" and "minute" mode, \nso please avoid use the "minute" mode to plot a super long time period.')

term_input = input('Which type of plot would you like to see? [day/hour/minute]:')
type_in = type_input(term_input)
#print (type_in)







lines = search_date(date_input,file)
temp_plot,date_plot = file_open(file,lines,length_input,type_in)
figure(date_plot,temp_plot,type_in,date_input,length_input,file_read)
#print(temp_plot)
#print(date_plot)

















































































