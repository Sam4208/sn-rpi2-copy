import time
import datetime as dt
import sys
import re
import matplotlib.pyplot as plt

import numpy as np

"""
There are 650 Temperature logs per day, around 25-27 per hour, counted twice by hand, used the data at 2016-11-18 as example.
ther script is generated based on this number count
"""
temp = []
date = []
ymin = 20
ymax = 25


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
        new_data_time = last_lines[11:30]
        new_data_temp = float(last_lines[47:53])
        temp.append(new_data_temp)
        date.append(new_data_time)
        
        """
        print(new_data_time)
        print(new_data_temp)
        print(temp)
        print(date)
        """
    return temp, date

def figure (x,y,kind):
    
        
        fig,ax = plt.subplots()
        print(x)
        print(y)
        ax.plot(x,y,clip_on=False)
        if kind == 25:
            
            ax.xaxis.set_major_locator(plt.MaxNLocator(30))
        else:
            pass
        plt.yticks(fontsize = 6)
        plt.xticks(fontsize = 6 , rotation = -25)
        plt.xlabel('Date and Time (YYYY-MM-DD HH:MM:SS)')
    
        plt.ylabel('Temperature (C)')
        plt.title('Temperature/Time (Histortical data)')
        ax.set_ylim(10,40)
    
        plt.show()
    
    
    
        
        
    

date_input = input('which day would you like to see (YYYY-MM-DD) :')
length_input = int(input ('How long would you see the plot for? (in hours) :'))
print('\nAs an expaination, the option "day" would plot a temperature-time graph with one data point per day, start from your choice of day. \nthe option "hour" would plot a temperature-time graph with one data point per hour, starting from 0:00 of your choice of day. \nthe option "minute" would plot a temperature-time graph with one data point per 4 minutes, starting from 0:00 of your choice of day.')
print('\nAs an precautiuon to a super massy x-axis, only 30 locators are allowed in the "hour" mode, so please be aware of that, also the MaxNLocator limit is NOT implemented on the "day" and "minute" mode, \nso please avoid use the "minute" mode to plot a super long time period.')

term_input = input('Which type of plot would you like to see? [day/hour/minute]:')
type_in = type_input(term_input)
#print (type_in)







lines = search_date(date_input,"/home/supernemo/TemperatureLogs/Temp_Ch0.txt")
temp_plot,date_plot = file_open("/home/supernemo/TemperatureLogs/Temp_Ch0.txt",lines,length_input,type_in)
figure(date_plot,temp_plot,type_in)
#print(temp_plot)
#print(date_plot)
